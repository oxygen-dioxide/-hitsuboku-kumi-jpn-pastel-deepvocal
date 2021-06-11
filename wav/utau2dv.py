#2019/7/17 v1.0
#2019/7/20 v1.1 修复有时候程序无法正常结束，导致dvcfg不完整的bug
import os
import sys
import time

def wavlen(wavpath):
    import contextlib
    import wave
    with contextlib.closing(wave.open(wavpath, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

print("utau2dv音源转换器v1.1单音阶版 by oxygendioxide")

#载入dv字典文件
directory="\\".join(os.path.abspath(sys.argv[0]).split('\\')[:-1])

#载入拆音字典文件
temp=open(directory+"\\Symbol list.txt").read().split('\n')
cvvcdict=set()
for i in temp:
    if(i!=''):
        cvvcdict.add(i.split(',')[0])

#载入辅音列表
consonants=set(open(directory+"\\Unvoiced Consonant list.txt").read().split('\n')+open(directory+"\\Voiced Consonant list.txt").read().split('\n'))
consonants.discard('')
#载入元音列表
temp=open(directory+"\\Vowel list.txt").read().split('\n')
vowels=set()
for i in temp:
    if(i!=''):
        vowels.add(i.split(',')[0])

#载入尾音列表
tails=set(open(directory+"\\Tail symbol list.txt").read().split('\n')+['-'])
tails.discard('')

#载入oto.ini
#oto.ini格式：[文件名]=[别名],[左边界],[固定范围],[右边界],[先行声音],[重叠]
#oto词典的结构：{[别名]:[文件名],[左边界],[固定范围],[右边界],[先行声音],[重叠]}
#时间单位：毫秒
#左边界从wav开头算起，固定范围、先行声音、重叠从左边界算起，右边界从左边界算起,为负数。
temp=open(directory+"\\oto.ini",encoding="shift-jis").read().split('\n')
oto=dict()
for i in temp:
    i=i.replace('=',',').split(',')
    if len(i)>=7:
        key=i[1]
        value=[i[0],float(i[2]),float(i[3]),float(i[4]),float(i[5]),float(i[6])]
        if(value[3]>0):
            value[3]=-wavlen(i[0])+value[1]+value[3]
        oto[key]=value



#写入dvcfg
if(os.path.isfile(directory+"\\voice.dvcfg")):
    input("voice.dvcfg已存在，继续运行将覆盖，是否继续？（按Enter继续）")

pitch=input("输入deepvocal中的音阶\n")
t=time.gmtime()
t="{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec)

dvcfg=open(directory+"\\voice.dvcfg","w",encoding="utf8")
dvcfg.write("{\n")
#CV
#connectPoint一定是0.05999999865889549
#endTime:VEP+0.06
#preutterance:PP-CP+0.06
#startTime:CP-0.06
#tailPoint:VEP-CP+0.115
#vowelEnd:VEP-CP+0.06
#vowelStart:VSP-CP+0.06
n=0
for i in cvvcdict:
    if((i in vowels) and (("- "+i) in oto.keys())):
        j="- "+i
    else:
        j=i
    if(j in oto.keys()):
        wavoto=oto[j]
        if n>0 :
            dvcfg.write(',\n')
        dvcfg.write('   "{}->{}" : '.format(pitch,i)+'{\n')
        dvcfg.write('      "connectPoint" : 0.05999999865889549,\n')
        dvcfg.write('      "endTime" : {:.16f},\n'.format(wavoto[1]/1000+wavoto[3]/1000+0.06))
        dvcfg.write('      "pitch" : "{}",\n'.format(pitch))
        dvcfg.write('      "preutterance" : {:.16f},\n'.format(wavoto[4]/1000+0.06))
        dvcfg.write('      "srcType" : "CV",\n')
        dvcfg.write('      "startTime" : {:.16f},\n'.format(wavoto[1]/1000-0.06))
        dvcfg.write('      "symbol" : "{}",\n'.format(i))
        dvcfg.write('      "tailPoint" : {:.16f},\n'.format(-wavoto[3]/1000+0.115))
        dvcfg.write('      "updateTime" : "{}",\n'.format(t))
        dvcfg.write('      "vowelEnd" : {:.16f},\n'.format(-wavoto[3]/1000+0.06))
        dvcfg.write('      "vowelStart" : {:.16f},\n'.format(wavoto[2]/1000+0.06))
        dvcfg.write('      "wavName" : "{}"\n'.format(wavoto[0]))
        dvcfg.write("   }")
        n+=1
    else:
        print(i+'缺失')
#-CV
for i in cvvcdict:
    if(("- "+i) in oto.keys()):
        wavoto=oto["- "+i]
        dvcfg.write(',\n')
        dvcfg.write('   "{}->{}" : '.format(pitch,"-"+i)+'{\n')
        dvcfg.write('      "connectPoint" : 0.05999999865889549,\n')
        dvcfg.write('      "endTime" : {:.16f},\n'.format(wavoto[1]/1000+wavoto[3]/1000+0.06))
        dvcfg.write('      "pitch" : "{}",\n'.format(pitch))
        dvcfg.write('      "preutterance" : {:.16f},\n'.format(wavoto[4]/1000+0.06))
        dvcfg.write('      "srcType" : "CV",\n')
        dvcfg.write('      "startTime" : {:.16f},\n'.format(wavoto[1]/1000-0.06))
        dvcfg.write('      "symbol" : "{}",\n'.format("-"+i))
        dvcfg.write('      "tailPoint" : {:.16f},\n'.format(-wavoto[3]/1000+0.115))
        dvcfg.write('      "updateTime" : "{}",\n'.format(t))
        dvcfg.write('      "vowelEnd" : {:.16f},\n'.format(-wavoto[3]/1000+0.06))
        dvcfg.write('      "vowelStart" : {:.16f},\n'.format(wavoto[2]/1000+0.06))
        dvcfg.write('      "wavName" : "{}"\n'.format(wavoto[0]))
        dvcfg.write("   }")
    else:
        print("- "+i+'缺失')
#VC
#connectPoint一定是0.05999999865889549
#endTime:EP
#startTime:SP-0.06
#tailPoint:EP-SP
for consonant in consonants:
    for vowel in vowels:
        if((vowel+' '+consonant)in oto.keys()):
            wavoto=oto[vowel+' '+consonant]
            dvcfg.write(',\n')
            dvcfg.write('   "{}->{}_{}" : '.format(pitch,vowel,consonant)+'{\n')
            dvcfg.write('      "connectPoint" : 0.05999999865889549,\n')
            dvcfg.write('      "endTime" : {:.16f},\n'.format(wavoto[1]/1000-wavoto[3]/1000))
            dvcfg.write('      "pitch" : "{}",\n'.format(pitch))
            dvcfg.write('      "srcType" : "VX",\n')
            dvcfg.write('      "startTime" : {:.16f},\n'.format(wavoto[1]/1000+wavoto[5]/1000-0.06))
            dvcfg.write('      "symbol" : "{}_{}",\n'.format(vowel,consonant))
            dvcfg.write('      "tailPoint" : {:.16f},\n'.format(wavoto[2]/1000-wavoto[5]/1000+0.06))
            dvcfg.write('      "updateTime" : "{}",\n'.format(t))
            dvcfg.write('      "wavName" : "{}"\n'.format(wavoto[0]))
            dvcfg.write("   }")
        else:
            print(vowel+' '+consonant+'缺失')
#VV
for consonant in vowels:
    for vowel in vowels:
        if((vowel+' '+consonant)in oto.keys()):
            wavoto=oto[vowel+' '+consonant]
            dvcfg.write(',\n')
            dvcfg.write('   "{}->{}_{}" : '.format(pitch,vowel,consonant)+'{\n')
            dvcfg.write('      "connectPoint" : 0.05999999865889549,\n')
            dvcfg.write('      "endTime" : {:.16f},\n'.format(wavoto[1]/1000-wavoto[3]/1000))
            dvcfg.write('      "pitch" : "{}",\n'.format(pitch))
            dvcfg.write('      "srcType" : "VX",\n')
            dvcfg.write('      "startTime" : {:.16f},\n'.format(wavoto[1]/1000+wavoto[5]/1000-0.06))
            dvcfg.write('      "symbol" : "{}_{}",\n'.format(vowel,consonant))
            dvcfg.write('      "tailPoint" : {:.16f},\n'.format(wavoto[2]/1000-wavoto[5]/1000+0.06))
            dvcfg.write('      "updateTime" : "{}",\n'.format(t))
            dvcfg.write('      "wavName" : "{}"\n'.format(wavoto[0]))
            dvcfg.write("   }")
        else:
            print(vowel+' '+consonant+'缺失')
#VX
for consonant in tails:
    for vowel in vowels:
        if((vowel+' '+consonant)in oto.keys()):
            wavoto=oto[vowel+' '+consonant]
            dvcfg.write(',\n')
            dvcfg.write('   "{}->{}_{}" : '.format(pitch,vowel,consonant)+'{\n')
            dvcfg.write('      "connectPoint" : 0.05999999865889549,\n')
            dvcfg.write('      "endTime" : {:.16f},\n'.format(wavoto[1]/1000-wavoto[3]/1000))
            dvcfg.write('      "pitch" : "{}",\n'.format(pitch))
            dvcfg.write('      "srcType" : "VX",\n')
            dvcfg.write('      "startTime" : {:.16f},\n'.format(wavoto[1]/1000+wavoto[5]/1000-0.06))
            dvcfg.write('      "symbol" : "{}_{}",\n'.format(vowel,consonant))
            dvcfg.write('      "tailPoint" : {:.16f},\n'.format(-wavoto[3]/1000-wavoto[5]/1000))
            dvcfg.write('      "updateTime" : "{}",\n'.format(t))
            dvcfg.write('      "wavName" : "{}"\n'.format(wavoto[0]))
            dvcfg.write("   }")
        else:
            print(vowel+' '+consonant+'缺失')
dvcfg.write("\n}")
dvcfg.close()
input("转换完成")
