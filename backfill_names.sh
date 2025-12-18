#!/bin/bash

# ============================================================================
# Backfill Display Names - Easy Runner Script
# ============================================================================
#
# This script makes it easy to backfill display_name for existing documents.
#
# Usage:
#   ./backfill_names.sh              # Run backfill
#   ./backfill_names.sh --dry-run    # Preview only
#   ./backfill_names.sh --help       # Show help
#
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# ============================================================================
# Main Script
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  Document Name Backfill Script                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/backfill_display_names.py" ]; then
    print_error "backfill_display_names.py not found!"
    print_info "Make sure you're in the project root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "python3 not found!"
    print_info "Please install Python 3"
    exit 1
fi

# Parse arguments
DRY_RUN=""
if [ "$1" == "--dry-run" ]; then
    DRY_RUN="--dry-run"
    print_warning "DRY RUN MODE - No changes will be made"
    echo ""
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    print_info "Usage:"
    echo "  ./backfill_names.sh              Run backfill"
    echo "  ./backfill_names.sh --dry-run    Preview only (no changes)"
    echo "  ./backfill_names.sh --help       Show this help"
    echo ""
    print_info "Examples:"
    echo "  ./backfill_names.sh --dry-run    # Preview changes first"
    echo "  ./backfill_names.sh               # Then apply changes"
    echo ""
    exit 0
fi

# Change to backend directory
cd backend

# Check environment variables
if [ -z "$SUPABASE_URL" ]; then
    print_warning "SUPABASE_URL not set"
    print_info "Trying to load from env.local.configured..."
    
    if [ -f "env.local.configured" ]; then
        export $(cat env.local.configured | grep -v '^#' | xargs)
        print_success "Environment loaded"
    else
        print_error "env.local.configured not found"
        print_info "Please set SUPABASE_URL and SUPABASE_SERVICE_KEY"
        exit 1
    fi
fi

# Show confirmation if not dry-run
if [ -z "$DRY_RUN" ]; then
    echo ""
    print_warning "This will update ALL documents without display_name"
    echo ""
    read -p "Continue? (y/N) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cancelled"
        exit 0
    fi
    echo ""
fi

# Run the backfill script
print_info "Running backfill script..."
echo ""

if python3 backfill_display_names.py $DRY_RUN; then
    echo ""
    print_success "Backfill complete!"
    
    if [ -n "$DRY_RUN" ]; then
        echo ""
        print_info "This was a dry run. To apply changes, run:"
        echo "  ./backfill_names.sh"
    else
        echo ""
        print_success "All done! Your documents now have clean names."
        print_info "Update your UI to use 'display_name' instead of 'filename'"
        print_info "See: frontend/DISPLAY_NAME_UI_EXAMPLE.tsx"
    fi
else
    echo ""
    print_error "Backfill failed"
    print_info "Check the error messages above"
    exit 1
fi

echo ""


