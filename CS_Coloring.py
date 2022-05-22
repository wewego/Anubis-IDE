import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def formatting(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages

STYLES2 = {
    'keyword': formatting([200, 120, 50], 'bold'),
    'keywordsTwo': formatting([30, 120, 110]),
    'operator': formatting([150, 150, 150]),
    'brace': formatting('darkGray'),
    'string': formatting([20, 110, 100]),
    #'string2': format([30, 120, 110]),
    'comment': formatting([128, 128, 128]),
    'numbers': formatting([100, 150, 190]),
}
STYLES3 = {
       'keyword': formatting('blue'),
       'keywordsTwo' : formatting('violet'),
      'operator': formatting('darkblue'),
       'brace': formatting('darkblue'),
       'string': formatting('magenta'),    
       'comment': formatting('grey'),
       'numbers': formatting('brown'),
   }

class CSharpHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # C# keywords

    
    keywords = [
        'and', 'break', 'continue',
        'else', 'finally','private','public','typeof','protected'
        'for', 'from', 'global', 'if', 'import', 'in','do','params',
        'is','not', 'or', 'pass','default','base','interface',
         'return', 'try', 'while', 'yield','checked','foreach','goto','get',
        'None', 'True', 'False','Button','using','namespace','new','try',
        'catch','throw','implicit','await','abstract','case','continue','switch',
        'sizeof','typeof','this','WriteLine','ReadLine'
    ]
    keywordsTwo= ['enum','void','class','int','string',
                  'float','double','decimal','const',
                  'long','bool','short','char','static','struct','var','Console']

    # C# operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # C# braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',';',"\'",'\"']

    def __init__(self, document):
        print("highlighter")
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.starting = (QRegExp("/\*"), 1, STYLES3['comment'])
        self.ending = (QRegExp("\*/"), 1, STYLES3['comment'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES3['keyword'])
                  for w in CSharpHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES3['operator'])
                  for o in CSharpHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES3['brace'])
                  for b in CSharpHighlighter.braces]
        rules += [(r'\b%s\b' % w, 0, STYLES3['keywordsTwo'])
                  for w in CSharpHighlighter.keywordsTwo]

        # All other rules
        rules += [

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES3['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'.'", 0, STYLES3['string']),


            # From '#' until a newline
            (r'//[^\n]*', 0, STYLES3['comment']),
            (r'/\*[^"\\]*(\\.[^"\\]*)*\*/', 0, STYLES3['comment']),


            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES3['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES3['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES3['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        #in_multiline = self.match_multiline(text, *self.tri_single)
        #if not in_multiline:
        self.match_multiline(text, *self.starting,*self.ending)

    def match_multiline(self, text, delimiter, in_state, style,delimiterEnd, in_stateEnd, styleEnd):
        
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiterEnd.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiterEnd.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
