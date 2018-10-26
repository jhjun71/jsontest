import json, os
import formtojson

from itertools import chain

KEYWORD = ['상호(법인명)', '사업자등록번호', '성명(대표자)', '주민(법인)등록번호', '사업장소재지']
THIS_YEAR = '2018년'
# X_MARGIN = 5
# Y_MARGIN = 10
# YEAR_MARGIN = 500

#json 파일이 들어있는 폴더 경로
dir_path = "C:\\Users\\User\\Desktop\\전진하\\1_참여기업_사업자등록증명\\1A_35_20181018"

#bizId가 들어있는 TXT 파일
in_file_name = "C:\\Users\\User\\Desktop\\전진하\\1A_35_20181018.txt"

#각 bizId 별로 결과 TXT 파일
out_file_name = "C:\\Users\\User\\Desktop\\전진하\\1_참여기업_사업자등록증명\\1A_35_20181018\\1A_35_20181018_out.txt"


#사업자등록증명에서 정보 뽑아내기
def parseRegistrationform (json_obj):

	#Given keyword, get the corresponding content from registration form
	content_list = formtojson.getContentFromKey (json_obj, KEYWORD)

	# if '' in content_list:
	# 	content_list = formtojson.findMissingValue (json_obj, content_list)

	print (content_list)


# with open(in_file_name, 'r') as file:
# 	for line in file:
# 		bizId = line.strip()
# 		print (bizId)#임시
# 		json_file_name = dir_path+'\\' + bizId + '.txt'
# 		if os.path.exists(json_file_name):
# 			print (json_file_name)#임시
# 			f = open(json_file_name, mode='rt', encoding='utf-8')
# 			json_obj = json.loads (f.read())
# 			values = []
# 			for keyw in KEYWORD:
# 				values.append (formtojson.getValueFromKey(json_obj, keyw, False))
# 				# print (values)
# 			values.append (formtojson.getValueFromKey(json_obj, THIS_YEAR, True))

# 			#위에서 나온 값 중 None이 있는 곳을 다시 찾기
# 			# print (values)
# 			added_value = formtojson.findMissingValue (json_obj, values)				
# 			# print (added_value)
			
# 			string_to_add = ''
# 			for v in values: 
# 				if (v != None): 
# 					string_to_add += v
# 				else:
# 					string_to_add += ''
# 				string_to_add += ','

# 			file_lines = [''.join([bizId, ',', string_to_add, '\n'])]

# 			with open(out_file_name, mode='a', encoding='utf-8') as out_f:
# 				out_f.writelines(file_lines)
# 	out_f.close()
# file.close()


TEST_JSON = 'C:\\Users\\User\\Desktop\\전진하\\1_참여기업_사업자등록증명\\1A_35_20181018\\622-81-06972.txt'
f = open(TEST_JSON, mode='rt', encoding='utf-8')

json_obj = json.loads (f.read())

parseRegistrationform (json_obj)
