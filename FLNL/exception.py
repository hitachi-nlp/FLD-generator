class FormalLogicExceptionBase(Exception):

    def __init__(self, message, *args, **kwargs):
        lines = message.split('\n')
        lines_with_indents = ['    ' + line for line in lines]
        message_with_indents = '\n'.join(lines_with_indents)

        message_with_class_name = '\n'.join([
            str(type(self).__name__) + '(',
            message_with_indents,
            ')',
        ])

        super().__init__(message_with_class_name, *args, **kwargs)
