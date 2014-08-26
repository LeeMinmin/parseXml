__author__ = 'min'

import codecs
import xml.etree.ElementTree as ET
from datetime import date
from pyh import *
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def parsexml(xml, img_list):
    allresult = []
    f = codecs.open(xml, 'r', 'utf-8')
    tree = ET.parse(f);
    root = tree.getroot()
    k = 0
    for child in root:
        ts = []
        for tc in child.getiterator('testcase'):
            tcClass = tc.get('classname')
            tcName = tc.get('name')
            if len(tc) == 1:
                tr = 'failed'
                for msg in tc.getchildren():
                    fmsg = msg.text
                img_url = img_list[k]
                k += 1
            else:
                tr = 'passed'
                fmsg = ''
                img_url = ''
            tcresult = {
                'testcase': tcName,
                'testclass': tcClass,
                'testresult': tr,
                'fmsg': fmsg,
                'img_url': img_url
            }
            ts.append(tcresult)
        allresult.append(ts)
    f.close()
    return allresult


def calbyclass(testclass, ts):
    passNum = 0
    failNum = 0
    for i in range(len(ts)):
        if ts[i]['testclass'] == testclass:
            if ts[i]['testresult'] == 'passed':
                passNum += 1
            else:
                failNum += 1
    cbc = {
        'passed': passNum,
        'failed': failNum,
        'total': passNum + failNum
    }
    return cbc


def classlist(ts):
    clist = []
    for i in range(len(ts)):
        clist.append(ts[i]['testclass'])
    cl = list(set(clist))
    return cl


def totalstat(allresult):
    statdata = {}
    llen = len(allresult)
    tpass = 0
    tfail = 0

    for i in range(llen):
        for j in range(len(allresult[i])):
            if allresult[i][j]['testresult'] == 'passed':
                tpass += 1
            else:
                tfail += 1
    statdata['totalpass'] = tpass
    statdata['totalfail'] = tfail
    statdata['total'] = tpass + tfail
    statdata['radio'] = str(float(tpass)/(tpass+tfail)*100)[:5] + '%'
    return statdata


def createhtml(xml, projectjob, img_list):
    localdir = ''
    allresult = parsexml(xml, img_list)
    tslen = len(allresult)
    page = PyH(projectjob + u"Robotium Daily Test Report")
    headfile = open(localdir + 'head.txt', 'r')
    head = headfile.read()
    statdata = totalstat(allresult)

    page << head
    div1 = page << div(cl='heading', id='div1')
    div1 << h1(projectjob+u' Daily Robotium Test Report') + p('<strong>Start Time:</strong> %s' %date.today()) + p('<strong>Status:</strong> PASS %s Failed %s PASS Ratio: %s'  %(str(statdata['totalpass']),str(statdata['totalfail']),statdata['radio']))
    div1 << p('<strong>Details view:</strong> %s' %(buildlink))

    table1 = page << table(id='result_table')
    headtr = table1 << tr(id='head_row', bgcolor='#8B7D7B')
    headtr << td('Test Group/Test case') + td('Total') + td('Passed')+td('Failed')
    totaltr = table1 << tr(id='totsl_row',bgcolor='#87CEEB')
    totaltr << td('<strong>Summary </strong>') + td('%s'%str(statdata['totalpass']+statdata['totalfail'])) + td('%s'%str(statdata['totalpass'])) + td('%s'%str(statdata['totalfail']))

    for i in range(tslen):
        #print Tresult[i]
        clist=classlist(allresult[i])
        for testclass in clist:
            classtr= table1 << tr(id='failclass',bgcolor='#FFE4B5')
            classtr << td('%s' %testclass)
            cstat = calbyclass(testclass, allresult[i])
            #print cstat
            classtr << td('%s' %cstat['total'])
            classtr << td('%s' %cstat['passed'])
            classtr << td('%s' %cstat['failed'])
            for j in range(len(allresult[i])):
                if allresult[i][j]['testclass'] == testclass:
                    tctr = classtr << tr(id='pt1.1', bgcolor='#ADD8E6')
                    tctr << ul(id='testcase')
                    tctr << td(id='none') << div(id='testcase') << p('%s' %allresult[i][j]['testcase'])
                    if(allresult[i][j]['fmsg'] != ''):
                        tctr << td(id='none', colspan='5', align='center') << div(id='testcase') << p('%s' % (allresult[i][j]['testresult'] + '<br/><a href="img/'+ allresult[i][j]['img_url'] +'">'+ allresult[i][j]['img_url'] +'<a/><br/>' + allresult[i][j]['fmsg']))
                    else:
                        tctr << td(id='none', colspan='5', align='center') << div(id='testcase') << p('%s' % allresult[i][j]['testresult'])
    #page.printOut()
    return page


def exportFile(source, target):
    cmd = 'adb pull ' + source + ' ' + target
    os.system(cmd)


def deleteFile(file):
    cmd = 'adb shell rm -r ' + file
    os.system(cmd)


def start_test():
    cmd = 'adb shell am instrument -e class com.umipay.android.umipaysdkdemo.test.FullSuite -w com.umipay.android.umipaysdkdemo.test/com.neenbedankt.android.test.InstrumentationTestRunner'
    res = os.system(cmd)
    return res

if __name__ == "__main__":
    result = start_test()
    if result == 0:
        sourceXml = 'data/data/com.umipay.android.umipaysdkdemo/files/TEST-all.xml'
        target_path = '/home/min/workspace/htmlReports/'
        exportFile(sourceXml, target_path)
        xmf = target_path + 'TEST-all.xml'
        sourceImg = 'sdcard/Robotium-ScreenShots'
        target_img_path = '/home/min/workspace/htmlReports/img/'
        exportFile(sourceImg, target_img_path)
        img_list = os.listdir(target_img_path)
        img_list.reverse()
        projectjob = '/home/min/workspace/htmlReports/testReport'
        temphtml = projectjob + '.html'
        buildlink = ''
        page = createhtml(xmf, projectjob, img_list)
        page.printOut(temphtml)
        deleteFile(sourceImg)
        deleteFile(sourceXml)
        print "testdone"
