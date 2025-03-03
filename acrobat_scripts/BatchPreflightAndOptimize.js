/**
 * BatchPreflightAndOptimize.js
 * 
 * Adobe Acrobat JavaScript to batch process PDFs with Preflight fixups 
 * and optimization.
 * 
 * This script:
 * 1. Fixes potential font problems
 * 2. Fixes problems in PDF tagging structure
 * 3. Optimizes documents with compatible settings
 * 
 * Usage in Acrobat Pro:
 * 1. Open Tools > JavaScript > JavaScript Editor
 * 2. Paste this script and save it
 * 3. Run with: app.trustedFunction(function(){app.addMenuItem({
 *    cName: "Batch Preflight and Optimize", 
 *    cParent: "File", 
 *    cExec: "batchPreflightAndOptimize()",
 *    cEnable: "event.rc = (app.activeDocs.length > 0);"
 *    })});
 */

// Helper for logging with timestamps
function logMessage(message) {
    var now = new Date();
    console.println("[" + now.toLocaleTimeString() + "] " + message);
}

// Run a single Preflight profile on current document
function runPreflightFixup(profileName) {
    try {
        if (typeof app.trustedHasSecurityPermission !== "function" || 
            !app.trustedHasSecurityPermission("com.adobe.acrobat.preflight")) {
            throw new Error("Insufficient permissions for Preflight");
        }
        
        // Get available profiles
        var profiles = app.getPreflightProfiles();
        var targetProfile = null;
        
        // Find the requested profile
        for (var i = 0; i < profiles.length; i++) {
            if (profiles[i].name === profileName) {
                targetProfile = profiles[i];
                break;
            }
        }
        
        if (!targetProfile) {
            logMessage("Error: Preflight profile '" + profileName + "' not found.");
            return false;
        }
        
        // Execute the profile
        var options = {
            noUI: true, // Run without UI
            errorWindow: false // Suppress error report
        };
        
        logMessage("Running Preflight profile: " + profileName);
        var result = app.activeDocs[0].preflight(targetProfile, options);
        
        // Process result
        if (result && result.errors && result.errors.length > 0) {
            logMessage("Preflight found " + result.errors.length + " issues.");
            return false;
        } else {
            logMessage("Preflight completed successfully.");
            return true;
        }
    } catch (e) {
        logMessage("Error during Preflight: " + e.toString());
        return false;
    }
}

// Fix font problems in current document
function fixFontProblems() {
    return runPreflightFixup("Fix potential font problems");
}

// Fix tagging structure in current document
function fixTaggingStructure() {
    return runPreflightFixup("Fix problems in PDF tagging structure");
}

// Optimize the current document using PDF Optimizer
function optimizeDocument(settings) {
    try {
        if (!app.trustedHasSecurityPermission("com.adobe.acrobat.pdfoptimizer")) {
            throw new Error("Insufficient permissions for PDF Optimizer");
        }
        
        var doc = app.activeDocs[0];
        
        // Default settings if none provided
        if (!settings) {
            settings = {
                colorImages: {
                    compression: "JPEG2000",
                    quality: 80,
                    resolution: 150
                },
                grayscaleImages: {
                    compression: "JPEG2000",
                    quality: 80,
                    resolution: 150
                },
                monochromeImages: {
                    compression: "JBIG2",
                    resolution: 300
                },
                cleanUp: {
                    optimizeDocument: true,
                    removeHiddenLayers: true,
                    flattenFormFields: false,
                    removeBookmarks: false,
                    removeAnnotations: false,
                    removeJavaScript: false
                }
            };
        }
        
        logMessage("Optimizing document...");
        var success = doc.optimize(settings);
        
        if (success) {
            logMessage("Optimization completed successfully.");
            return true;
        } else {
            logMessage("Optimization failed.");
            return false;
        }
    } catch (e) {
        logMessage("Error during optimization: " + e.toString());
        return false;
    }
}

// Process a single document with all fixups
function processDocument(doc) {
    try {
        // Activate the document
        doc.bringToFront();
        logMessage("Processing: " + doc.documentFileName);
        
        // Run font fixes
        if (!fixFontProblems()) {
            logMessage("Font fixes had warnings or errors, continuing...");
        }
        
        // Run tagging structure fixes
        if (!fixTaggingStructure()) {
            logMessage("Tag structure fixes had warnings or errors, continuing...");
        }
        
        // Optimize the document
        if (!optimizeDocument()) {
            logMessage("Optimization had warnings or errors, continuing...");
        }
        
        // Save the document
        doc.save();
        logMessage("Saved: " + doc.documentFileName);
        
        return true;
    } catch (e) {
        logMessage("Error processing document: " + e.toString());
        return false;
    }
}

// Main function to run batch processing
function batchPreflightAndOptimize() {
    app.beginPriv();
    try {
        var docs = app.activeDocs;
        
        if (docs.length === 0) {
            app.alert("No documents are open.");
            return;
        }
        
        console.clear();
        logMessage("Starting batch Preflight and optimization for " + docs.length + " documents...");
        
        var successCount = 0;
        
        // Process each document
        for (var i = 0; i < docs.length; i++) {
            if (processDocument(docs[i])) {
                successCount++;
            }
        }
        
        logMessage("Batch processing complete. Successfully processed " + 
                   successCount + " out of " + docs.length + " documents.");
                   
        app.alert("Batch processing complete.\nSuccessfully processed " + 
                  successCount + " out of " + docs.length + " documents." +
                  "\nCheck the JavaScript Console for details.");
    } catch (e) {
        console.println("Error in batch processing: " + e.toString());
        app.alert("Error in batch processing: " + e.message);
    } finally {
        app.endPriv();
    }
}