"""
This class creates an instance of the Trigno base. Put your key and license here.
"""
import clr
clr.AddReference("./DataServer/resources/DelsysAPI")
clr.AddReference("System.Collections")

from Aero import AeroPy

key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABMwuuAWq0IxAskFsKKskokvB5ZVh9urqcYQ3ZNHPVgQUcKz50DoCY2PmM3tj/W3cfOX3XKaaCXG7ppAWTBQDhq8="
license = "<License>"\
        "<Id>89b523fd-df31-4de3-965c-566f80f02024</Id>"\
        "<Type>Standard</Type>"\
        "<Quantity>10</Quantity>"\
        "<LicenseAttributes>"\
        "<Attribute name='Software'></Attribute>"\
        "</LicenseAttributes>"\
        "<ProductFeatures>"\
        "<Feature name='Sales'>True</Feature>"\
        "<Feature name='Billing'>False</Feature>"\
        "</ProductFeatures>"\
        "<Customer>"\
        "<Name>Pablo A. Iturralde </Name>"\
        "<Email>pablo.iturralde@ucu.edu.uy</Email>"\
        "</Customer>"\
        "<Expiration>Wed, 31 Dec 2031 05:00:00 GMT</Expiration>"\
        "<Signature>MEQCICWbys7iocoXZrmXlv51NPqbJyF3MxLh9gCbGCagustdAiAvz3lTm89s8yP/zpIrxJP7tMQ9hLa8zLL8w+v1zgVvOQ==</Signature>"\
        "</License>"

class TrignoBase():
    def __init__(self):
        self.BaseInstance = AeroPy()
       