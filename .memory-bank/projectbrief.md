# ePubs Accessibility Enhancement Project Brief

## Project Overview
The ePubs Accessibility Enhancement Project is a comprehensive toolkit for enhancing document accessibility across academic and historical publications. The system provides specialized tools for PDF processing, OCR enhancement, accessibility compliance validation, and **automated WCAG/PDF-UA/ADA compliance generation through machine learning**.

## Core Objectives
1. **Universal Accessibility**: Transform documents to meet PDF/UA-1 compliance standards
2. **Academic Specialization**: Handle complex academic layouts, mathematical content, tables, citations
3. **Historical Document Processing**: Optimize OCR for degraded text and historical terminology  
4. **Workflow Automation**: Provide end-to-end processing pipelines from acquisition to enhancement
5. **🎯 NEW: Automated Compliance Generation**: Train ML models using 1600+ compliant PDFs to automatically generate WCAG/PDF-UA/ADA compliant accessibility structures

## Project Structure
- **Scraper Component**: Document acquisition from library resources (Purdue focus)
- **Processor Component**: Core document enhancement engine with unified architecture
- **Data Pipeline**: Input/output processing with sample academic papers
- **🆕 Accessibility Training System**: ML training infrastructure for automated compliance generation

## Technical Foundation
- **Language**: Python 3.9+ with modern packaging (pyproject.toml)
- **Core Libraries**: PyMuPDF, pikepdf, ocrmypdf for PDF processing
- **Architecture**: Service container pattern with dependency injection
- **Processing**: Sequential enhancement pipeline (OCR → Metadata → Accessibility)
- **🆕 ML Training**: Phase 2B extension with FAISS vector database, hierarchical caching, and accessibility pattern learning

## Enhanced Project Scope
This is a monorepo containing all components required for document accessibility enhancement AND automated accessibility compliance generation, designed for academic research institutions and digital libraries requiring scalable accessibility compliance at institutional scale.

## Success Criteria
1. PDF/UA-1 compliant output documents
2. Automated OCR and font embedding
3. Screen reader optimized content structure
4. Scalable processing for document collections
5. Docker containerization for deployment consistency
6. **🎯 NEW: >90% accuracy in automated WCAG/PDF-UA/ADA compliance generation**
7. **🎯 NEW: >95% compliance rate for automatically generated accessibility structures**
