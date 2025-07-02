#!/bin/bash
# Corrected Cloud Enhancement Batch Processor
# Uses proper direct-argument CLI syntax

echo "🚀 Starting Cloud Enhancement Batch Processing (Syntax Corrected)"
echo "Input Directory: data/input/"
echo "Output Directory: data/output/cloud_enhanced/"
echo "Enhancement Mode: Adobe AutoTag (Cloud)"
echo "Reports: Disabled (as requested)"
echo "================================================================"

# Configure Adobe PDF Services credentials
export PDF_SERVICES_CLIENT_ID="323b58e452f143aeaadcf48af365a9a6"
export PDF_SERVICES_CLIENT_SECRET="p8e-feTlYh6VoHXgpe9k39VHhPHiEDdalAhn"

# Create output directory structure
mkdir -p data/output/cloud_enhanced

# Initialize processing metrics
success_count=0
error_count=0
total_files=$(find data/input -name "*.pdf" | wc -l)

echo "📊 Processing $total_files PDF files with corrected CLI syntax..."
echo ""

# Systematic file processing loop
for pdf_file in data/input/*.pdf; do
    # File existence validation
    if [ ! -f "$pdf_file" ]; then
        echo "⚠️  No PDF files found in data/input/"
        break
    fi
    
    # File path construction
    filename=$(basename "$pdf_file" .pdf)
    output_file="data/output/cloud_enhanced/${filename}_enhanced.pdf"
    
    echo "📄 Processing: $filename"
    echo "   Input:  $pdf_file"
    echo "   Output: $output_file"
    
    # CORRECTED CLI COMMAND (removed "process" subcommand)
    epubs \
        "$pdf_file" \
        "$output_file" \
        --mode academic \
        --use-adobe-autotag \
        --no-generate-accessibility-report \
        --shift-headings \
        --verbose
    
    # Result validation and metrics tracking
    if [ $? -eq 0 ]; then
        echo "   ✅ Success: $filename processed with cloud enhancement"
        ((success_count++))
    else
        echo "   ❌ Error: Failed to process $filename"
        ((error_count++))
    fi
    echo ""
done

# Processing completion analysis and reporting
echo "🎯 Batch Processing Complete"
echo "================================================================"
echo "Total Files: $total_files"
echo "Successfully Processed: $success_count"
echo "Processing Errors: $error_count"
echo "Success Rate: $(( success_count * 100 / total_files ))%"
echo "Output Location: data/output/cloud_enhanced/"

# Output verification
if [ $success_count -gt 0 ]; then
    echo ""
    echo "📁 Enhanced PDFs Created:"
    ls -la data/output/cloud_enhanced/*.pdf 2>/dev/null | head -5
    if [ $(ls data/output/cloud_enhanced/*.pdf 2>/dev/null | wc -l) -gt 5 ]; then
        echo "   ... and $(($(ls data/output/cloud_enhanced/*.pdf 2>/dev/null | wc -l) - 5)) more files"
    fi
fi
