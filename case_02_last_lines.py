import io
import os
from unittest import TestCase


def last_lines(filename, buffer_size=io.DEFAULT_BUFFER_SIZE):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()

        while remaining_size > 0:
            offset = min(file_size, offset + buffer_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buffer_size))
            remaining_size -= buffer_size
            lines = buffer.splitlines(keepends=True)

            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment


class TestLastLines(TestCase):
    def test_last_lines_invert_file(self):
        line = last_lines('files/last_lines.txt')

        self.assertEqual(next(line), 'And this is line 4\n')
        self.assertEqual(next(line), 'This is line 3\n')
        self.assertEqual(next(line), 'This is line 2\n')
        self.assertEqual(next(line), 'This is a file\n')

    def test_apply_buffer_size(self):
        line = last_lines('files/last_lines.txt', buffer_size=10)

        self.assertEqual(next(line), 'And this is line 4\n')
        self.assertEqual(next(line), 'This is line 3\n')
        self.assertEqual(next(line), 'This is line 2\n')
        self.assertEqual(next(line), 'This is a file\n')
