import base64


class Util:

    def b64_decrypt(self, encode_string):
        b64_bytes = encode_string.encode("ascii")
        decode_bytes = base64.b64decode(b64_bytes)
        decode_string = decode_bytes.decode("ascii")
        return decode_string

    def b64_encrypt(self, plain_text):
        b64_bytes = plain_text.encode("ascii")
        encode_bytes = base64.b64encode(b64_bytes)
        encode_string = encode_bytes.decode("ascii")
        return encode_string