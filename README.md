# text-frequency-analyzer
A script that reads text and finds the most common words, demonstrating file I/O, string processing, and data structures.

To run:
- Run the run-sample.txt script
- Feel free to use the command inside as inspiration to analyze your own files

Notes on how this was developed:
- I was looking for an idea to code, so I asked Claude to recommend one.  This is what it suggested.  It went ahead and generated the code for me. I figured I shouldn't look a gift horse in the mouth, so I took it as my starting point.
- I asked Claude to update the original code to use pydantic.
- I asked Claude to generate unit tests
- Those tests had three strikes against them:
  - They had a lot of tests for trivial code
  - The tests themselves were complex
  - They were failing
- So I removed the tests for the trivial parts and fixed the remaining tests to get them passing
- I wanted to code something on my own, so I decided to switch the application from using argparse to using typer (though admittedly I still asked Claude for pointers on the typer syntax)