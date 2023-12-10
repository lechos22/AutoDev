class CodeFragmentData:
    def __init__(self, path: str, fragment_id: int, content: str, line_start: int, line_end: int):
        self.path = path
        self.fragment_id = fragment_id
        self.content = content
        self.line_start = line_start
        self.line_end = line_end
        self.description = ''

    def set_description(self, desc: str):
        self.description = desc
