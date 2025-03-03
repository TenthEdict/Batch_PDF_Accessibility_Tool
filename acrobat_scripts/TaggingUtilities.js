/**
 * TaggingUtilities.js
 * 
 * Adobe Acrobat JavaScript utility functions for PDF tagging 
 * and accessibility adjustments.
 * 
 * This script provides tools to:
 * 1. Fix headings that were incorrectly tagged
 * 2. Apply custom tagging templates to academic documents
 * 3. Add alt text to images and complex figures
 * 4. Fix table structures
 * 
 * Usage in Acrobat Pro:
 * 1. Open Tools > JavaScript > JavaScript Editor
 * 2. Paste this script and save it
 * 3. Run with: app.trustedFunction(function(){app.addMenuItem({
 *    cName: "Tagging Utilities", 
 *    cParent: "Advanced",
 *    cExec: "showTaggingUtilitiesDialog()",
 *    cEnable: "event.rc = (app.activeDocs.length > 0);"
 *    })});
 */

// Helper for logging with timestamps
function logMessage(message) {
    var now = new Date();
    console.println("[" + now.toLocaleTimeString() + "] " + message);
}

// Get the document's tag structure
function getDocumentStructure() {
    var doc = app.activeDocs[0];
    
    // Check if document is tagged
    if (!doc.isTagged()) {
        return null;
    }
    
    try {
        var structure = {};
        var tags = doc.tags;
        
        // Count tag types
        var tagCounts = {};
        for (var i = 0; i < tags.length; i++) {
            var tagName = tags[i].name;
            if (!tagCounts[tagName]) {
                tagCounts[tagName] = 1;
            } else {
                tagCounts[tagName]++;
            }
        }
        
        structure.tagCounts = tagCounts;
        structure.totalTags = tags.length;
        
        // Check for common issues
        structure.issues = {
            emptyAltText: 0,
            missingHeadingLevels: false,
            emptyTableCells: 0
        };
        
        // Check for empty alt text in figures
        for (var i = 0; i < tags.length; i++) {
            if (tags[i].name === "Figure") {
                var altText = tags[i].altText;
                if (!altText || altText === "") {
                    structure.issues.emptyAltText++;
                }
            }
            
            // Check for empty table cells
            if (tags[i].name === "TD" || tags[i].name === "TH") {
                var children = tags[i].children;
                if (!children || children.length === 0) {
                    structure.issues.emptyTableCells++;
                }
            }
        }
        
        // Check for heading level hierarchy issues
        var headingLevels = [];
        for (var i = 0; i < tags.length; i++) {
            if (tags[i].name.match(/^H\d$/)) {
                var level = parseInt(tags[i].name.substring(1));
                headingLevels.push(level);
            }
        }
        
        // Sort heading levels
        headingLevels.sort();
        
        // Check if we have heading levels with gaps
        if (headingLevels.length > 0) {
            var minLevel = headingLevels[0];
            var maxLevel = headingLevels[headingLevels.length - 1];
            
            for (var i = minLevel; i <= maxLevel; i++) {
                if (headingLevels.indexOf(i) === -1) {
                    structure.issues.missingHeadingLevels = true;
                    break;
                }
            }
        }
        
        return structure;
    } catch (e) {
        console.println("Error analyzing document structure: " + e.toString());
        return null;
    }
}

// Fix heading tags in document
function fixHeadingTags() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        if (!doc.isTagged()) {
            logMessage("Document is not tagged. Please tag the document first.");
            return false;
        }
        
        logMessage("Analyzing document headings...");
        
        var tags = doc.tags;
        var headings = [];
        
        // Find all heading tags
        for (var i = 0; i < tags.length; i++) {
            if (tags[i].name.match(/^H\d$/)) {
                headings.push(tags[i]);
            }
        }
        
        if (headings.length === 0) {
            logMessage("No heading tags found in document.");
            return false;
        }
        
        logMessage("Found " + headings.length + " headings.");
        
        // Check for heading level order issues
        var currentLevel = 0;
        var fixCount = 0;
        
        for (var i = 0; i < headings.length; i++) {
            var level = parseInt(headings[i].name.substring(1));
            
            // First heading should be H1
            if (i === 0 && level !== 1) {
                logMessage("First heading should be H1, but found " + headings[i].name);
                headings[i].name = "H1";
                fixCount++;
                currentLevel = 1;
                continue;
            }
            
            // Other headings should not skip levels
            if (level > currentLevel + 1) {
                logMessage("Heading level skip detected: " + headings[i].name);
                var newLevel = currentLevel + 1;
                headings[i].name = "H" + newLevel;
                fixCount++;
                currentLevel = newLevel;
            } else {
                currentLevel = level;
            }
        }
        
        if (fixCount > 0) {
            logMessage("Fixed " + fixCount + " heading level issues.");
            return true;
        } else {
            logMessage("No heading level issues found.");
            return true;
        }
    } catch (e) {
        logMessage("Error fixing heading tags: " + e.toString());
        return false;
    } finally {
        app.endPriv();
    }
}

// Fix empty table cells
function fixTableCells() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        if (!doc.isTagged()) {
            logMessage("Document is not tagged. Please tag the document first.");
            return false;
        }
        
        logMessage("Analyzing table cells...");
        
        var tags = doc.tags;
        var emptyCells = [];
        
        // Find all empty table cells
        for (var i = 0; i < tags.length; i++) {
            if ((tags[i].name === "TD" || tags[i].name === "TH") && 
                (!tags[i].children || tags[i].children.length === 0)) {
                emptyCells.push(tags[i]);
            }
        }
        
        if (emptyCells.length === 0) {
            logMessage("No empty table cells found.");
            return true;
        }
        
        logMessage("Found " + emptyCells.length + " empty table cells.");
        
        // Fix empty cells by adding a Span tag with a non-breaking space
        for (var i = 0; i < emptyCells.length; i++) {
            var spanTag = emptyCells[i].createChild(-1, "Span");
            spanTag.value = "\u00A0"; // Non-breaking space
        }
        
        logMessage("Fixed " + emptyCells.length + " empty table cells.");
        return true;
    } catch (e) {
        logMessage("Error fixing table cells: " + e.toString());
        return false;
    } finally {
        app.endPriv();
    }
}

// Apply academic document structure template
function applyAcademicTemplate() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        if (!doc.isTagged()) {
            logMessage("Document is not tagged. Please tag the document first.");
            return false;
        }
        
        logMessage("Analyzing document for academic structure...");
        
        var tags = doc.tags;
        var rootTag = null;
        
        // Find document root tag
        for (var i = 0; i < tags.length; i++) {
            if (tags[i].name === "Document") {
                rootTag = tags[i];
                break;
            }
        }
        
        if (!rootTag) {
            logMessage("Document root tag not found.");
            return false;
        }
        
        // Check if we have a title
        var titleFound = false;
        var abstractFound = false;
        var bodyFound = false;
        
        var children = rootTag.children;
        for (var i = 0; i < children.length; i++) {
            var childName = children[i].name;
            
            if (childName === "H1") {
                titleFound = true;
            } else if (childName === "Sect" && children[i].title === "Abstract") {
                abstractFound = true;
            } else if (childName === "Sect" && children[i].title === "Body") {
                bodyFound = true;
            }
        }
        
        // Add missing academic structure elements
        if (!titleFound && tags.length > 0) {
            // Look for potential title in the first paragraphs
            var potentialTitle = null;
            for (var i = 0; i < Math.min(5, tags.length); i++) {
                if (tags[i].name === "P") {
                    potentialTitle = tags[i];
                    break;
                }
            }
            
            if (potentialTitle) {
                logMessage("Converting potential title paragraph to H1 heading.");
                potentialTitle.name = "H1";
            }
        }
        
        // Reorganize structure if needed
        if (!abstractFound || !bodyFound) {
            // Look for Abstract and Body sections by content
            var sections = [];
            for (var i = 0; i < tags.length; i++) {
                if (tags[i].name === "Sect") {
                    sections.push(tags[i]);
                }
            }
            
            if (sections.length > 1 && !abstractFound) {
                // First section might be abstract
                logMessage("Setting first section as Abstract.");
                sections[0].title = "Abstract";
            }
            
            if (sections.length > 2 && !bodyFound) {
                // Second section might be body
                logMessage("Setting second section as Body.");
                sections[1].title = "Body";
            }
        }
        
        logMessage("Academic document template applied.");
        return true;
    } catch (e) {
        logMessage("Error applying academic template: " + e.toString());
        return false;
    } finally {
        app.endPriv();
    }
}

// Add alt text to all figures without it
function addAltTextToFigures() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        if (!doc.isTagged()) {
            logMessage("Document is not tagged. Please tag the document first.");
            return false;
        }
        
        logMessage("Finding figures without alt text...");
        
        var tags = doc.tags;
        var figuresWithoutAlt = [];
        
        // Find all figures without alt text
        for (var i = 0; i < tags.length; i++) {
            if (tags[i].name === "Figure" && (!tags[i].altText || tags[i].altText === "")) {
                figuresWithoutAlt.push(tags[i]);
            }
        }
        
        if (figuresWithoutAlt.length === 0) {
            logMessage("No figures without alt text found.");
            return true;
        }
        
        logMessage("Found " + figuresWithoutAlt.length + " figures without alt text.");
        
        // Get page number and figure number for each figure
        for (var i = 0; i < figuresWithoutAlt.length; i++) {
            var figNum = i + 1;
            var pageNum = getTagPageNumber(figuresWithoutAlt[i]);
            
            // Add placeholder alt text
            var altText = "Figure " + figNum + " on page " + pageNum + ". [REQUIRES DESCRIPTION]";
            figuresWithoutAlt[i].altText = altText;
            
            logMessage("Added placeholder alt text to figure " + figNum + " on page " + pageNum);
        }
        
        logMessage("Added placeholder alt text to " + figuresWithoutAlt.length + " figures.");
        app.alert("Added placeholder alt text to " + figuresWithoutAlt.length + " figures.\n\nPlease review and update the placeholder text with appropriate descriptions.");
        
        return true;
    } catch (e) {
        logMessage("Error adding alt text to figures: " + e.toString());
        return false;
    } finally {
        app.endPriv();
    }
}

// Helper to get a tag's page number
function getTagPageNumber(tag) {
    try {
        var doc = app.activeDocs[0];
        
        if (tag && tag.rect) {
            var rect = tag.rect;
            var pageNum = doc.getPageNumFromRect(rect);
            
            return pageNum + 1; // Convert to 1-based page number
        }
        
        return "unknown";
    } catch (e) {
        return "unknown";
    }
}

// Run auto tag with better settings
function enhancedAutoTag() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        // Check if already tagged
        if (doc.isTagged()) {
            var response = app.alert(
                "Document already has tags. Remove existing tags and re-tag?",
                1, // Yes-No dialog
                "Tagging Confirmation"
            );
            
            if (response !== 1) { // Not "Yes"
                return false;
            }
            
            // Remove existing tags
            doc.removeTags();
        }
        
        logMessage("Starting enhanced auto-tagging...");
        
        // Get document language
        var lang = doc.language;
        if (!lang || lang === "") {
            lang = "ENU"; // Default to English US
            logMessage("No document language set, using English (US).");
        }
        
        // Auto-tag the document with optimal settings
        var tagOptions = {
            language: lang,
            headings: true,
            tables: true,
            figures: true,
            lists: true
        };
        
        doc.autotag(tagOptions);
        
        logMessage("Auto-tagging complete.");
        
        // Fix common issues
        fixHeadingTags();
        fixTableCells();
        
        // Save the document
        doc.save();
        logMessage("Document saved with enhanced tags.");
        
        return true;
    } catch (e) {
        logMessage("Error during enhanced auto-tagging: " + e.toString());
        return false;
    } finally {
        app.endPriv();
    }
}

// Show dialog with tagging utilities
function showTaggingUtilitiesDialog() {
    app.beginPriv();
    try {
        var dialog = {
            initialize: function(dialog) {
                var doc = app.activeDocs[0];
                dialog.load({
                    "isTagged": doc.isTagged()
                });
                
                // Disable buttons if document is not tagged
                if (!doc.isTagged()) {
                    dialog.enable({
                        "analyze": true,
                        "enhancedAutoTag": true,
                        "fixHeadings": false,
                        "fixTables": false,
                        "applyTemplate": false,
                        "addAltText": false
                    });
                }
            },
            analyze: function(dialog) {
                var structure = getDocumentStructure();
                
                if (!structure) {
                    app.alert("Document is not tagged or structure cannot be analyzed.");
                    return;
                }
                
                // Create report
                var report = "Document Structure Analysis\n";
                report += "==========================\n\n";
                report += "Total tags: " + structure.totalTags + "\n\n";
                
                report += "Tag counts:\n";
                for (var tag in structure.tagCounts) {
                    report += "- " + tag + ": " + structure.tagCounts[tag] + "\n";
                }
                
                report += "\nIssues found:\n";
                report += "- Figures without alt text: " + structure.issues.emptyAltText + "\n";
                report += "- Missing heading levels: " + (structure.issues.missingHeadingLevels ? "Yes" : "No") + "\n";
                report += "- Empty table cells: " + structure.issues.emptyTableCells + "\n";
                
                console.clear();
                console.println(report);
                app.alert("Analysis complete. See JavaScript Console for full report.");
            },
            enhancedAutoTag: function(dialog) {
                enhancedAutoTag();
                
                // Refresh dialog after tagging
                dialog.load({
                    "isTagged": app.activeDocs[0].isTagged()
                });
                
                dialog.enable({
                    "analyze": true,
                    "enhancedAutoTag": true,
                    "fixHeadings": true,
                    "fixTables": true,
                    "applyTemplate": true,
                    "addAltText": true
                });
            },
            fixHeadings: function(dialog) {
                fixHeadingTags();
            },
            fixTables: function(dialog) {
                fixTableCells();
            },
            applyTemplate: function(dialog) {
                applyAcademicTemplate();
            },
            addAltText: function(dialog) {
                addAltTextToFigures();
            }
        };
        
        app.execDialog({
            cTitle: "PDF Tagging Utilities",
            cMsg: "Select a tagging operation to perform:",
            cParent: null,
            oKHand: dialog,
            cButtons: [
                ["analyze", "Analyze Document Structure"],
                ["enhancedAutoTag", "Enhanced Auto-Tag"],
                ["fixHeadings", "Fix Heading Structure"],
                ["fixTables", "Fix Table Cells"],
                ["applyTemplate", "Apply Academic Template"],
                ["addAltText", "Add Alt Text to Figures"],
                ["cancel", "Close"]
            ],
            oDefBtnNum: 0
        });
    } catch (e) {
        console.println("Error showing tagging utilities dialog: " + e.toString());
        app.alert("Error: " + e.message);
    } finally {
        app.endPriv();
    }
}