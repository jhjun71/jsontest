import json, re
from itertools import chain
from pprint import pprint

# KEYWORD = ['상호(법인명)', '사업자등록번호', '성명(대표자)', '사업장소재지', '2018년', '월', '일']
KEYWORD = ['상호(법인명)', '사업자등록번호', '성명(대표자)', '주민(법인)등록번호', '사업장소재지']
X_MARGIN = 5
Y_MARGIN = 10
YEAR_MARGIN = 1000
# PASS_RATE = .6


#From json, get the content given the keys
def getContentFromKey (json_obj, key_list):

	#get the clustered word list
	clustered_list = getCluster (json_obj)
	text_list = concat(clustered_list)

	#content from each key
	content_list = []

	# per key, find the index of the cluster start with key

	for key in key_list:
		for text in text_list:
			text_idx = -1
			content_idx = 0

			if text.startswith (key):
				# index of text in text_list in order to find the right cluster in clustered_list
				text_idx = text_list.index(text)
				# start index of the content in text string
				content_idx = text.index(key[-1])+1
				break
		if content_idx == 0:
			content_list.append ('')
		else:
			cluster = clustered_list[text_idx]
			# print (cluster)
			_list = []
			for word_info in cluster[content_idx:]:
				_list.append(word_info['text'])
			content_list.append (' '.join(_list))


	print (content_list)



	# per key, cluster and the index, get the remaining text



#concaternate the text from the clustered list
def concat(clustered_list):

	text_list = []
	for cluster in clustered_list:
		concat_text = ''
		for word_info in cluster:
			concat_text += word_info['text']
		text_list.append (concat_text)

	print (text_list)
	return text_list



def getCluster (json_obj):
	line_infos = [region["lines"] for region in json_obj["regions"]]
	word_infos = []
	for line in line_infos:
	    for word_metadata in line:
	        for word_info in word_metadata["words"]:
	            word_infos.append(word_info)
	
	# sort according to the y-coord
	word_infos.sort(key = lambda i: int(i['boundingBox'].split(',')[1]))
	return clusterFromY (word_infos)
	# print (word_infos)
	# return clusterFromY (word_infos)


def gatherText (word_list):
# 	# for i in word_list:
# 	# 	print (i['boundingBox'].split(',')[1])

# 	# print (word_list)
# 	# print ('\n')
	word_list.sort(key = lambda i: int(i['boundingBox'].split(',')[1]))
# 	# print (word_list)

# 	return word_list

	# sorted (word_list, key = lambda i: i['boundingBox'].split(',')[0])
	# print ('\n')
	# print (word_list)


#K-mean 구현
from statistics import mean
Y_ERROR = 5

def clusterFromY (word_list):
	clusters = [[]]

	for word_info in word_list:
		for cluster in clusters: #cluster is also a list
			m = meanFromCluster (cluster)

			if m==0 or abs(m-int(word_info['boundingBox'].split(',')[1])) < Y_ERROR:
				cluster.append (word_info)
				break
			elif clusters.index(cluster) == len (clusters)-1: 
				new_list = []
				new_list.append(word_info)
				clusters.append (new_list)
				break
			else:
				continue

	#x 좌표 순서대로 배열
	for cluster in clusters:
		cluster.sort(key = lambda i: int(i['boundingBox'].split(',')[0]))
		# for word_info in cluster:
		# 	print (word_info['text'], end = ' ')
		# print ('\n')

	print (clusters)
	return clusters






# word list로부터 y 좌표의 평균 구하기
def meanFromCluster (word_list):
	y_list = []
	for word_info in word_list:
		y_list.append (int(word_info['boundingBox'].split(',')[1]))

	if len (y_list) > 0:
		return mean (y_list)
	else:
		return 0

# 연속된 list에 None 이 있는 경우에 y 좌표를 찾아서 찾기
def findMissingValue (json_input, value_list):
	# print ('values are: ', value_list)
	

	x_coord_list = []
	y_coord_list = []

	if None in value_list:
		for v in value_list:
			if v != None:
				gen_coord = findCoord (json_input, v)
				coord = next(gen_coord, None).split(',')
				# if coord != None:
				x_coord_list.append (coord[0])
				y_coord_list.append (coord[1])
			else:
				x_coord_list.append (None)
				y_coord_list.append (None)
			# print (v, x_coord_list, y_coord_list)

		# print ('Y-coord: ', y_coord_list)

		y_gap = getDiffAverage (y_coord_list)

		if y_gap > 5 : # not too small
			missing_val_idx = value_list.index(None)
			# print ('First None is appreared at index = ', missing_val_idx)

			if missing_val_idx != 0:
				# print (int(x_coord_list[missing_val_idx-1]), int(y_coord_list[missing_val_idx-1])+y_gap)
				text_g = findText(json_input, int(x_coord_list[missing_val_idx-1]), int(y_coord_list[missing_val_idx-1])+y_gap, False, False)
			else:
				# print (int(x_coord_list[1]), int(y_coord_list[1])-y_gap)
				non_none_idx = 1
				while y_coord_list[non_none_idx] == None:
					non_none_idx += 1  #y_coord_list에 non-None 이 0/1 인 것은 제외 됨
				text_g = findText(json_input, int(x_coord_list[non_none_idx]), int(y_coord_list[non_none_idx])-y_gap, False, False)
			
			value_list[missing_val_idx] = next(text_g, None)

			print (value_list)
	
	return value_list


	

# None 아닌 element 들끼리 빼서 평균을 돌려줌 
def getDiffAverage (value_list):
	diffAvgList = []
	l = len(value_list)

	if (value_list.count(None) < l-1): # can't find one or two non-None values in the list

		for index, v in enumerate (value_list):
			while v == None and index < l-1:
				index += 1

			init_idx = index
			init_val = value_list[index]
			# print (init_idx, init_val)


			if init_idx != l-1: #all values are None

				final_idx = init_idx+1
				final_val = value_list [final_idx]

				while final_val == None and final_idx < l-1:
					final_idx += 1
					final_val = value_list [final_idx]
					# print (final_idx, final_val)
				if final_val != None:
					diffAvgList.append ((int(final_val)-int(init_val))/(final_idx-init_idx))

		# print (diffAvgList)
		return (sum(diffAvgList)/len(diffAvgList))
	else:
		return 0




def getValueFromKey (json_input, key_string, y_gap):
	g_1 = findCoord(json_input, key_string)
	coordList = next(g_1, None)
	# while coordList != None:
	# 	coord = coordList.split(',')
	# 	g_2 = findText (json_input, int(coord[0]), int(coord[1]), True, y_gap)
	# 	text = next(g_2, None)
	# 	string_to_find = ''
	# 	while text != None:
	# 		string_to_find += text		
	# 		text = next(g_2, None)
	# 	print (string_to_find)
	# 	if string_to_find == None:
	# 		coordList = next (g_1, None)
	# 	else: #found		
	# 		return string_to_find
	string_to_find = ''
	if coordList != None:
		coord = coordList.split(',')
		g_2 = findText (json_input, int(coord[0]), int(coord[1]), True, y_gap)
		text = next(g_2, None)
		# string_to_find = ''
		while text != None:
			string_to_find += text		
			text = next(g_2, None)

	if string_to_find == '':
		string_to_find = None

	return string_to_find


#이 함수는 특정 키워드를 가진 words의 좌표를 return
def findCoord(json_input, lookup_key):
	if isinstance(json_input, dict):
		dictkeys = json_input.keys()
		if 'boundingBox' in dictkeys and 'words' in dictkeys and concatTextUnderWords (json_input['words']).startswith(lookup_key):
			yield json_input['boundingBox']
		for k in dictkeys:
			yield from findCoord (json_input[k], lookup_key)
	elif isinstance(json_input, list):
	    for item in json_input:
	        yield from findCoord(item, lookup_key)

#이 함수는 'words' 아래 있는 text를 다 붙여주는 함수
def concatTextUnderWords (json_input):
	if isinstance(json_input, list):
		concatText = ''
		for json_obj in json_input: 
			#여기서 item 은 dict임
			for k, v in json_obj.items():
				if k == 'text':	concatText += v
		return concatText
	else:
		return ''

#This function finds the boundingBox w/ y-coord within +-5 given y and returns string
def findText (json_input, x_coord, y_coord, x_gap, y_gap):
	if isinstance(json_input, dict):
		dictkeys = json_input.keys()
		if 'boundingBox' in dictkeys and 'words' in dictkeys:
			coordList = json_input['boundingBox'].split(',')
			if x_gap == True and y_gap == False:
				if abs(int(coordList[0])- x_coord)>X_MARGIN and abs(int(coordList[1])-y_coord) <Y_MARGIN: #키워드와 x 좌표가 차이나는 값
					yield concatTextUnderWords(json_input['words'])
			elif x_gap == False and y_gap == False:
				if abs(int(coordList[0])- x_coord)<X_MARGIN+20 and abs(int(coordList[1])-y_coord) <Y_MARGIN:
					yield concatTextUnderWords(json_input['words'])
			else:#y_gap == True
				if abs(int(coordList[0])- x_coord)<X_MARGIN and abs(int(coordList[1])-y_coord) <Y_MARGIN and y_coord > YEAR_MARGIN:
					yield concatTextUnderWords(json_input['words'])	
		for k in dictkeys:
			yield from findText (json_input[k], x_coord, y_coord, x_gap, y_gap)
	elif isinstance(json_input, list):
	    for item in json_input:
	        yield from findText(item, x_coord, y_coord, x_gap, y_gap)


TEST_JSON = 'C:\\Users\\User\\Desktop\\전진하\\606-86-13724.txt'
f = open(TEST_JSON, mode='rt', encoding='utf-8')

json_obj = json.loads (f.read())

getContentFromKey (json_obj, KEYWORD)

# example = [None, 7, None, 10.9, 13.01]
# print (getDiffAverage (example))

exam_string = [None,'606-86-13724',None,'180111-0654508',None]
# findMissingValue(json_obj, exam_string)
# 

# f = open('test1.txt', mode='rt', encoding='utf-8')

# json_obj = json.loads (f.read())

# 상호
# g = findCoord (json_obj, KEYWORD[0])
# coord_0 = next(g).split(',')
# g = findText (json_obj, int(coord_0[0]), int(coord_0[1]))
# companyName = next(g)
# print (companyName)

# g= findCoord (json_obj, KEYWORD[1])
# coord = next(g).split(',')
# g = findText (json_obj, int(coord[0]), int(coord[1]))
# bizId = next(g)
# print (bizId)

# g= findCoord (json_obj, KEYWORD[2])
# coord = next(g).split(',')
# g = findText (json_obj, int(coord[0]), int(coord[1]))
# ceoName = next(g)
# print (ceoName)


# delta_y = int(coord[1]) - int(coord_0[1])
# # print (delta_y)
# g = findText (json_obj, int (coord[0]) , int(coord[1])+delta_y)
# companyAddress = next (g)
# print (companyAddress)

# g = findCoord (json_obj, KEYWORD[4])
# coord_day = next(g).split(',')
# print (coord_day)
# if int(coord_day[1])>YEAR_MARGIN:
# 	g=findText (json_obj, int(coord_day[0]), int(coord_day[1]))
# 	print (next(g, None))

# print (getValueFromKey (json_obj, "개업일"))

# g = findCoord (json_obj, KEYWORD[3])
# print (next(g, None))




# g= findCoord (json_obj, KEYWORD[3])
# print (next(g))
# coord = next(g).split(',')
# g = findText (json_obj, int(coord[0]), int(coord[1]))
# companyAddress = next(g)
# print (companyAddress)


# jsonString = json.dumps(f.read(), indent=4)

# g = findCoord(json_obj, 'words')

# json_list = [{"boundingBox":"143,472,75,26","text":"상호"},{"boundingBox":"244,472,9,25","text":"("},
# {"boundingBox":"280,472,22,26","text":"법"},{"boundingBox":"330,472,22,25","text":"인"},{"boundingBox":"380,472,22,26","text":"명"},{"boundingBox":"431,472,9,26","text":")"}]

# if concatTextUnderWords (json_list) == KEYWORD1:
# 	print ('yes')
# else:
# 	print ('no')

# keys = json_obj.keys()
# if 'language' in keys and 'orientation' in keys:
# 	print('yes')
# else:
# 	print ('no')



