import struct


class BinaryProtocol:
    @staticmethod
    def encode_game_state(ball_x, ball_y, pad1_y, pad2_y, score1, score2):
        return struct.pack('!ffffII', ball_x, ball_y, pad1_y, pad2_y, score1, score2)

    @staticmethod
    def decode_game_state(data):
        return struct.unpack('!ffffII', data)
