from binascii import hexlify, unhexlify
import base64

from Crypto.Cipher import AES
from payment.backends.allpay.settings import settings


class InvalidBlockSizeError(Exception):
    """Raised for invalid block sizes"""
    pass


class PKCS7Encoder():
    """
    Technique for padding a string as defined in RFC 2315, section 10.3,
    note #2
    """

    def __init__(self, block_size=16):
        if block_size < 1 or block_size > 99:
            raise InvalidBlockSizeError('The block size must be between 1 '
                                        'and 99')
        self.block_size = block_size

    def encode(self, text):
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        pad = unhexlify('%02d' % amount_to_pad)
        return text + pad * amount_to_pad

    def decode(self, text):
        pad = int(hexlify(text[-1]))
        return text[:-pad]


def encrypt(message):
    padder = PKCS7Encoder(block_size=16)
    padded_message = padder.encode(message)
    aes = AES.new(settings.HashKey, AES.MODE_CBC, settings.HashIV)
    return base64.b64encode(aes.encrypt(padded_message))


def decrypt(encrypted_message):
    aes = AES.new(settings.HashKey, AES.MODE_CBC, settings.HashIV)
    padded_message = aes.decrypt(base64.b64decode(encrypted_message))
    padder = PKCS7Encoder()
    return padder.decode(padded_message)
