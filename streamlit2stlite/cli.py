import argparse
import sys
from pathlib import Path
from .core import convert_streamlit_to_stlite, extract_imports, STLITE_VERSION

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Convert Streamlit Python apps to stlite HTML apps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  streamlit2stlite my_app.py
      Converts my_app.py to my_app.html with auto-detected requirements

  streamlit2stlite my_app.py -o output.html
      Converts my_app.py to output.html

  streamlit2stlite my_app.py --requirements pandas,numpy,plotly
      Specifies exact requirements to install

  streamlit2stlite my_app.py --title "My Dashboard"
      Sets a custom page title

  streamlit2stlite my_app.py --stlite-version 0.80.0
      Uses a specific stlite version
'''
    )
    
    parser.add_argument(
        'input',
        type=str,
        help='Path to the input Streamlit Python file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Path to the output HTML file (default: same name as input with .html extension)'
    )
    
    parser.add_argument(
        '-r', '--requirements',
        type=str,
        default=None,
        help='Comma-separated list of pip packages to install (default: auto-detect from imports)'
    )
    
    parser.add_argument(
        '-t', '--title',
        type=str,
        default=None,
        help='Title for the HTML page (default: auto-detect from code)'
    )
    
    parser.add_argument(
        '--stlite-version',
        type=str,
        default=STLITE_VERSION,
        help=f'Version of stlite to use (default: {STLITE_VERSION})'
    )
    
    parser.add_argument(
        '--add-requirements',
        type=str,
        default=None,
        help='Additional requirements to add to auto-detected ones (comma-separated)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print verbose output'
    )
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Check extension merely as a warning
    if not input_path.suffix.lower() == '.py':
        # Just a warning, proceed anyway
        pass
    
    try:
        python_code = input_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.html')
    
    # Parse requirements
    requirements = None
    if args.requirements:
        requirements = [r.strip() for r in args.requirements.split(',') if r.strip()]
    
    # Add additional requirements if specified
    if args.add_requirements:
        additional = [r.strip() for r in args.add_requirements.split(',') if r.strip()]
        if requirements is None:
            requirements = extract_imports(python_code)
        requirements = list(set(requirements + additional))
    
    # Verbose output
    if args.verbose:
        print(f"Input: {input_path}")
        print(f"Output: {output_path}")
        if requirements is None:
            detected_reqs = extract_imports(python_code)
            print(f"Auto-detected requirements: {detected_reqs}")
        else:
            print(f"Using requirements: {requirements}")
        print(f"stlite version: {args.stlite_version}")
    
    # Convert
    try:
        html_content = convert_streamlit_to_stlite(
            python_code=python_code,
            title=args.title,
            requirements=requirements,
            stlite_version=args.stlite_version
        )
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write output
    try:
        output_path.write_text(html_content, encoding='utf-8')
        print(f"Successfully converted '{input_path}' to '{output_path}'")
        
        if args.verbose:
            # Show final requirements used if we haven't already
            if requirements is None:
                 print(f"Final requirements used: {extract_imports(python_code)}")
            
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
