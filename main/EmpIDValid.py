import http.client
import xml.etree.ElementTree  as ET


class classEmpIDValid:
    def __init__(self):
        self.userName = ''
        self.userDept = ''
    
    def Search(self, userID):
        headers = {'Content-Type': 'application/xml'}
        body = '<ZHRA_J8080><COMPANY>300</COMPANY><BUSINESS_UNIT>300BU</BUSINESS_UNIT><EMPLID></EMPLID><GUBUN>C</GUBUN><DESC>{}</DESC><ZZ_PROPERTY_03>01</ZZ_PROPERTY_03><ZZ_REQUEST_DT></ZZ_REQUEST_DT><USER_ID></USER_ID><ACCESS_IP></ACCESS_IP><PG_ID></PG_ID></ZHRA_J8080>'.format(userID)

        conn = http.client.HTTPSConnection('hihr.hhi.co.kr')
        conn.request('POST','/EHR/ZHRA_J8080/searchList/selectEmpList', body, headers)
        res = conn.getresponse()

        data = res.read()
        dataDecode = data.decode('utf-8')

        nodeTree = ET.fromstring(dataDecode)
        self.userName = nodeTree.find('ZHRA_J8080').find('EMP_NAME').text
        self.userDept = nodeTree.find('ZHRA_J8080').find('DEPTNAME').text
        self.userPos = nodeTree.find('ZHRA_J8080').find('ZZ_POSITION_NM').text
