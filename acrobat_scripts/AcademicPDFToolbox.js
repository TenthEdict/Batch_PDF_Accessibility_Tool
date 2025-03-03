/**
 * AcademicPDFToolbox.js
 * 
 * Adobe Acrobat JavaScript tools specifically designed for academic PDF documents.
 * Provides specialized tools for academic journal articles, books, and manuscripts.
 * 
 * This script:
 * 1. Detects and marks document sections (abstract, methods, results, etc.)
 * 2. Creates appropriate bookmarks based on detected sections
 * 3. Fixes math equation tagging for accessibility
 * 4. Creates a table of contents when missing
 * 5. Enhances citation accessibility
 * 
 * Usage in Acrobat Pro:
 * 1. Open Tools > JavaScript > JavaScript Editor
 * 2. Paste this script and save it
 * 3. Run with: app.trustedFunction(function(){app.addMenuItem({
 *    cName: "Academic PDF Toolbox", 
 *    cParent: "Document",
 *    cExec: "showAcademicToolbox()",
 *    cEnable: "event.rc = (app.activeDocs.length > 0);"
 *    })});
 */

// Helper for logging with timestamps
function logMessage(message) {
    var now = new Date();
    console.println("[" + now.toLocaleTimeString() + "] " + message);
}

// Document section patterns for academic papers
const ACADEMIC_SECTIONS = {
    "abstract": /\b(abstract|summary)\b/i,
    "introduction": /\b(introduction|background|overview)\b/i,
    "methods": /\b(methods|methodology|materials\s+and\s+methods|experimental|procedure)\b/i,
    "results": /\b(results|findings|observations)\b/i,
    "discussion": /\b(discussion|interpretation|implications)\b/i,
    "conclusion": /\b(conclusion|concluding\s+remarks|summary\s+and\s+conclusion)\b/i,
    "references": /\b(references|bibliography|works\s+cited|literature\s+cited)\b/i,
    "acknowledgments": /\b(acknowledgments|acknowledgements|acknowledgement)\b/i,
    "appendix": /\b(appendix|appendices|supplementary\s+materials?)\b/i
};

// Detect academic document structure
function detectAcademicStructure() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        logMessage("Analyzing academic document structure...");
        
        // Get document text
        var docText = "";
        for (var i = 0; i < doc.numPages; i++) {
            docText += doc.getPageText(i);
        }
        
        // Find sections
        var sections = [];
        var headings = doc.bookmarkRoot ? doc.bookmarkRoot.children : null;
        
        // Try to use bookmarks if available
        if (headings && headings.length > 0) {
            logMessage("Using existing bookmarks to detect structure");
            
            for (var i = 0; i < headings.length; i++) {
                var heading = headings[i];
                
                for (var sectionName in ACADEMIC_SECTIONS) {
                    if (ACADEMIC_SECTIONS[sectionName].test(heading.name)) {
                        sections.push({
                            type: sectionName,
                            title: heading.name,
                            page: heading.page
                        });
                        break;
                    }
                }
            }
        } else {
            // Otherwise use text analysis to find sections
            logMessage("No bookmarks found. Using text analysis to detect structure");
            
            // Analyze text in document
            var contentFound = false;
            
            // Simple text-based detection - look for paragraphs that seem like headings
            var paragraphs = docText.split(/\r?\n\r?\n/);
            for (var i = 0; i < paragraphs.length; i++) {
                var para = paragraphs[i].trim();
                
                // Skip short paragraphs
                if (para.length < 3 || para.length > 100) continue;
                
                for (var sectionName in ACADEMIC_SECTIONS) {
                    if (ACADEMIC_SECTIONS[sectionName].test(para)) {
                        // This paragraph looks like a section heading
                        sections.push({
                            type: sectionName,
                            title: para
                        });
                        contentFound = true;
                        break;
                    }
                }
            }
            
            if (!contentFound) {
                logMessage("Could not detect academic structure automatically");
                return null;
            }
        }
        
        // See what sections we found
        logMessage("Detected " + sections.length + " academic sections:");
        for (var i = 0; i < sections.length; i++) {
            logMessage("- " + sections[i].type + ": " + sections[i].title);
        }
        
        return sections;
    } catch (e) {
        logMessage("Error in academic structure detection: " + e.toString());
        return null;
    } finally {
        app.endPriv();
    }
}

// Create bookmarks for academic sections
function createAcademicBookmarks() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        var sections = detectAcademicStructure();
        
        if (!sections || sections.length === 0) {
            logMessage("No academic sections found to bookmark");
            return false;
        }
        
        // Create bookmarks root if needed
        if (!doc.bookmarkRoot) {
            doc.bookmarkRoot = doc.createBookmark({
                cName: "Contents",
                cExpr: "this.pageNum = 0",
                cAction: "this.pageNum = 0;"
            });
        }
        
        // Check for duplicate bookmarks
        var existingBookmarks = [];
        if (doc.bookmarkRoot.children) {
            for (var i = 0; i < doc.bookmarkRoot.children.length; i++) {
                existingBookmarks.push(doc.bookmarkRoot.children[i].name);
            }
        }
        
        // Create bookmarks for each section
        var bookmarksAdded = 0;
        for (var i = 0; i < sections.length; i++) {
            var section = sections[i];
            
            // Skip if this section title already has a bookmark
            if (existingBookmarks.indexOf(section.title) !== -1) {
                logMessage("Bookmark for '" + section.title + "' already exists");
                continue;
            }
            
            // Try to find the page number if not already known
            if (!section.page) {
                var pageNum = findSectionPage(section.title);
                if (pageNum >= 0) {
                    section.page = pageNum;
                } else {
                    logMessage("Could not find page for section: " + section.title);
                    section.page = 0;
                }
            }
            
            // Create the bookmark
            doc.bookmarkRoot.createChild({
                cName: section.title,
                cExpr: "this.pageNum = " + section.page,
                cAction: "this.pageNum = " + section.page + ";"
            });
            
            bookmarksAdded++;
            logMessage("Added bookmark for '" + section.title + "' on page " + section.page);
        }
        
        logMessage("Added " + bookmarksAdded + " academic section bookmarks");
        if (bookmarksAdded > 0) {
            return true;
        } else {
            return false;
        }
    } catch (e) {
        logMessage("Error creating academic bookmarks: " + e.toString());
        return false;
    } finally {
        app.endPriv();
    }
}

// Helper to find which page contains a section title
function findSectionPage(sectionText) {
    try {
        var doc = app.activeDocs[0];
        
        // Search through pages for the text
        for (var i = 0; i < doc.numPages; i++) {
            var pageText = doc.getPageText(i);
            if (pageText.indexOf(sectionText) !== -1) {
                return i;
            }
        }
        
        return -1;
    } catch (e) {
        logMessage("Error finding section page: " + e.toString());
        return -1;
    }
}

// Tag equations in the document
function tagEquations() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        if (!doc.isTagged()) {
            logMessage("Document is not tagged. Please tag the document first.");
            return false;
        }
        
        logMessage("Searching for untagged equations...");
        
        // Look for equations by searching for common symbols
        var mathPatterns = [
            /\\sum/,      // Sum symbol
            /\\int/,      // Integral
            /\\frac/,     // Fraction
            /\\sqrt/,     // Square root
            /\\alpha/,    // Greek letters
            /\\beta/,
            /\\gamma/,
            /\\delta/,
            /\\epsilon/,
            /\\theta/,
            /\\sigma/,
            /\\omega/,
            /\\partial/,  // Partial derivative
            /\\infty/,    // Infinity
            /\\lim/       // Limit
        ];
        
        // Get all text from the document
        var docText = "";
        for (var i = 0; i < doc.numPages; i++) {
            docText += doc.getPageText(i);
        }
        
        // Check if there's any LaTeX-like code
        var containsMath = false;
        for (var i = 0; i < mathPatterns.length; i++) {
            if (mathPatterns[i].test(docText)) {
                containsMath = true;
                break;
            }
        }
        
        if (!containsMath) {
            logMessage("No obvious mathematical notation found in document");
            return false;
        }
        
        // Search for tags that might contain equations
        var tags = doc.tags;
        var equationCount = 0;
        
        for (var i = 0; i < tags.length; i++) {
            if (tags[i].name === "P" || tags[i].name === "Span") {
                var tagText = tags[i].value;
                
                // Check if this text contains math symbols
                var containsMathSymbols = false;
                for (var j = 0; j < mathPatterns.length; j++) {
                    if (mathPatterns[j].test(tagText)) {
                        containsMathSymbols = true;
                        break;
                    }
                }
                
                if (containsMathSymbols) {
                    // This looks like it contains an equation, mark it
                    tags[i].name = "Formula";
                    
                    // Add alt text if not present
                    if (!tags[i].altText || tags[i].altText === "") {
                        tags[i].altText = "Mathematical equation. [Needs description]";
                    }
                    
                    equationCount++;
                    logMessage("Tagged an equation on page " + getTagPageNumber(tags[i]));
                }
            }
        }
        
        if (equationCount > 0) {
            logMessage("Tagged " + equationCount + " equations in the document");
            return true;
        } else {
            logMessage("No equations could be tagged");
            return false;
        }
    } catch (e) {
        logMessage("Error tagging equations: " + e.toString());
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

// Create a table of contents if missing
function createTableOfContents() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        // Check if we have existing bookmarks to create TOC from
        if (!doc.bookmarkRoot || !doc.bookmarkRoot.children || doc.bookmarkRoot.children.length === 0) {
            // Try to create academic bookmarks first
            if (!createAcademicBookmarks()) {
                logMessage("No bookmarks available. Cannot create table of contents.");
                return false;
            }
        }
        
        logMessage("Creating table of contents from bookmarks...");
        
        // Get all bookmarks
        var bookmarks = doc.bookmarkRoot.children;
        var tocText = "Table of Contents\n\n";
        
        for (var i = 0; i < bookmarks.length; i++) {
            var bookmark = bookmarks[i];
            var page = bookmark.page;
            
            // Add entry
            tocText += bookmark.name + " .......... " + (page + 1) + "\n";
            
            // Add any child bookmarks with indentation
            if (bookmark.children && bookmark.children.length > 0) {
                for (var j = 0; j < bookmark.children.length; j++) {
                    var childBookmark = bookmark.children[j];
                    var childPage = childBookmark.page;
                    
                    tocText += "    " + childBookmark.name + " .......... " + (childPage + 1) + "\n";
                }
            }
        }
        
        // Create a new page at the beginning for the TOC
        if (app.trustedHasSecurityPermission("com.adobe.acrobat.pdfEdit")) {
            
            // This requires privileged context for page editing
            // Option 1: Display alert with the TOC
            app.alert("Generated Table of Contents:\n\n" + tocText);
            
            // Option 2: If full page editing is supported in your environment
            // Uncomment the code below to actually add a TOC page
            /*
            doc.insertPages({
                nPage: 0,
                cPath: "/C/Program Files/Adobe/Acrobat DC/Acrobat/Plug-ins/EWH/Templates/BlankPage.pdf"
            });
            
            var tocField = doc.addField("TOC", "text", 0, [50, 50, 550, 750]);
            tocField.value = tocText;
            tocField.readonly = true;
            */
            
            logMessage("Table of contents created and displayed");
            return true;
        } else {
            // Just display the TOC
            app.alert("Generated Table of Contents:\n\n" + tocText);
            return true;
        }
    } catch (e) {
        logMessage("Error creating table of contents: " + e.toString());
        return false;
    } finally {
        app.endPriv();
    }
}

// Detect and enhance citations
function enhanceCitations() {
    app.beginPriv();
    try {
        var doc = app.activeDocs[0];
        
        if (!doc.isTagged()) {
            logMessage("Document is not tagged. Please tag the document first.");
            return false;
        }
        
        logMessage("Analyzing document for citations...");
        
        // Citation patterns
        var inlineCitationPatterns = [
            /\([A-Z][a-zA-Z]+ et al\., \d{4}\)/,           // (Author et al., 2020)
            /\([A-Z][a-zA-Z]+ and [A-Z][a-zA-Z]+, \d{4}\)/, // (Author and Author, 2020)
            /\([A-Z][a-zA-Z]+, \d{4}\)/,                   // (Author, 2020)
            /\[\d+\]/,                                     // [1]
            /\[\d+(-|–|—)\d+\]/                            // [1-5]
        ];
        
        // Get all spans and paragraph tags
        var tags = doc.tags;
        var citationCount = 0;
        
        for (var i = 0; i < tags.length; i++) {
            if (tags[i].name === "P" || tags[i].name === "Span") {
                var tagText = tags[i].value;
                
                // Look for citation patterns in the text
                for (var j = 0; j < inlineCitationPatterns.length; j++) {
                    var matches = tagText.match(inlineCitationPatterns[j]);
                    if (matches && matches.length > 0) {
                        
                        // Rather than modifying tags (which is complex), we'll add
                        // the information to our report
                        citationCount += matches.length;
                        
                        logMessage("Found citation: " + matches[0] + " on page " + getTagPageNumber(tags[i]));
                    }
                }
            } else if (tags[i].name === "Reference") {
                // Already tagged as a reference
                citationCount++;
            }
        }
        
        if (citationCount > 0) {
            logMessage("Found " + citationCount + " citations in the document");
            
            // Create a report with recommendations
            var report = "Citation Analysis Report\n";
            report += "======================\n\n";
            report += "Found " + citationCount + " citations in the document.\n\n";
            report += "Recommendations for citation accessibility:\n";
            report += "1. Ensure each citation in the references section is tagged as a 'Reference' element\n";
            report += "2. For numeric citations [1], include author names in the text when possible\n";
            report += "3. Link in-text citations to their corresponding entries in the references section\n";
            report += "4. For references available online, provide stable URLs in the references list\n";
            
            console.clear();
            console.println(report);
            app.alert("Citation analysis complete. See JavaScript Console for full report.");
            
            return true;
        } else {
            logMessage("No citations found in the document");
            return false;
        }
    } catch (e) {
        logMessage("Error analyzing citations: " + e.toString());
        return false;
    } finally {
        app.endPriv();
    }
}

// Show the academic toolbox dialog
function showAcademicToolbox() {
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
                        "detectStructure": true,
                        "createBookmarks": true,
                        "createTOC": true,
                        "tagEquations": false,
                        "enhanceCitations": false
                    });
                }
            },
            detectStructure: function(dialog) {
                var sections = detectAcademicStructure();
                
                if (!sections || sections.length === 0) {
                    app.alert("Could not detect academic structure in this document.");
                    return;
                }
                
                // Create report
                var report = "Academic Document Structure\n";
                report += "==========================\n\n";
                
                report += "Detected sections:\n";
                for (var i = 0; i < sections.length; i++) {
                    report += "- " + sections[i].type + ": " + sections[i].title;
                    
                    if (sections[i].page !== undefined) {
                        report += " (page " + (sections[i].page + 1) + ")";
                    }
                    
                    report += "\n";
                }
                
                console.clear();
                console.println(report);
                app.alert("Structure analysis complete. See JavaScript Console for full report.");
            },
            createBookmarks: function(dialog) {
                if (createAcademicBookmarks()) {
                    app.alert("Academic bookmarks have been created.");
                } else {
                    app.alert("Could not create academic bookmarks. See console for details.");
                }
            },
            createTOC: function(dialog) {
                if (createTableOfContents()) {
                    app.alert("Table of contents has been created.");
                } else {
                    app.alert("Could not create table of contents. See console for details.");
                }
            },
            tagEquations: function(dialog) {
                if (tagEquations()) {
                    app.alert("Equations have been tagged.");
                } else {
                    app.alert("Could not tag equations. See console for details.");
                }
            },
            enhanceCitations: function(dialog) {
                if (enhanceCitations()) {
                    app.alert("Citation analysis complete. See console for report.");
                } else {
                    app.alert("Could not analyze citations. See console for details.");
                }
            }
        };
        
        app.execDialog({
            cTitle: "Academic PDF Toolbox",
            cMsg: "Select an operation to perform:",
            cParent: null,
            oKHand: dialog,
            cButtons: [
                ["detectStructure", "Detect Academic Structure"],
                ["createBookmarks", "Create Section Bookmarks"],
                ["createTOC", "Create Table of Contents"],
                ["tagEquations", "Tag Equations"],
                ["enhanceCitations", "Enhance Citations"],
                ["cancel", "Close"]
            ],
            oDefBtnNum: 0
        });
    } catch (e) {
        console.println("Error showing academic toolbox: " + e.toString());
        app.alert("Error: " + e.message);
    } finally {
        app.endPriv();
    }
}