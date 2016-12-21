#!usr/bin/python
#encoding=utf-8


import MySQLdb
import sys
import re
import json
import community
import datetime
import networkx as nx
import matplotlib.pyplot as plt
reload(sys)
sys.setdefaultencoding('utf-8')

"""
source database
"""
db_host = '127.0.0.1'
db_port = 3306
db_username = 'root'
db_password = 'mysql'
db_name = 'Freebuf_Secpulse'


record_limit = 20

def getMysqlConn():
	return MySQLdb.connect(host = db_host, user = db_username, passwd = db_password, db = db_name, port = db_port, charset = "utf8")


def closeDb(database = None):
	if not database:
		database.close()

def DelectCommit():
	mysqlConn = getMysqlConn()
	cursor = mysqlConn.cursor()

	sql = "delete from Community;"
	cursor.execute(sql)
	mysqlConn.commit()



def SelectRelation(id):
	mysqlConn = getMysqlConn()
	cur = mysqlConn.cursor()

	query_sql = "select * from SiteRelation where id >= " + str(id) + " order by id asc limit " + str(record_limit);
	cur.execute(query_sql)
	results = cur.fetchall()
	mysqlConn.close()
	return results


def SelectCommun(ComID):
	mysqlConn = getMysqlConn()
	cur = mysqlConn.cursor()

	query_sql = "select * from Community where CommunID = " + str(ComID) ;
	cur.execute(query_sql)
	results = cur.fetchall()
	mysqlConn.close()
	return results


def UpdateCenter(id):
	mysqlConn = getMysqlConn()
	cur = mysqlConn.cursor()

	query_sql = "update Community set isCenter = 1 where id = " + str(id) ;
	print query_sql
	cur.execute(query_sql)
	mysqlConn.commit()
	mysqlConn.close()


def InsertComm(items = []):
	mysqlConn = getMysqlConn()
	cursor = mysqlConn.cursor()

	insert_sql = "insert into Community(siteDomain,siteName,CommunID,indegree,createTime) "+"values(%s,%s,%s,%s,%s)"

	insert_item = []
	insert_item.append(items['siteDomain'])
	insert_item.append(items['siteName'])
	insert_item.append(items['CommunID'])
	insert_item.append(items['indegree'])
	insert_item.append(items['createTime'])
	print insert_item
	cursor.execute(insert_sql,insert_item)
	mysqlConn.commit()


def doGraph():
	bgid = 537
	T = nx.Graph()

	DelectCommit()

	results = SelectRelation(bgid)
	while results:
		for result in results:
			print result
			LinkCount = result[3]
			T.add_weighted_edges_from([(result[1], result[2], LinkCount)])
		bgid = result[0] + 1
		results = SelectRelation(bgid)
	
	partition = community.best_partition(T)
	#print "====================="
	#print partition

	SaveCommunity(partition,T)
	
	size = float(len(set(partition.values())))
	pos = nx.spring_layout(T)
	count = 0
	plt.title("站点关系网络")
	
	for com in set(partition.values()):
		count = count + 1
		list_nodes = [nodes for nodes in partition.keys()
				if partition[nodes] == com]                 
		nx.draw_networkx_nodes(T, pos, list_nodes, node_size = 40, with_labels = True,font_size = 8,node_color = str(count / size))
	

	nx.draw_networkx_edges(T,pos,with_labels = True, alpha=0.5 )
	plt.savefig("networkr_20161201_1.png")
	plt.show()

	

def SaveCommunity(parttit,Graph):
	items = {}
	for (k,v) in parttit.items():
		items['siteDomain'] = k
		items['siteName'] = k
		items['CommunID'] = v
		items['indegree'] = Graph.degree(k)
		items['createTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		InsertComm(items)
    	print 'Finish insert'+ '%s:%s' %(k, v)




"""
默认度最大的节点为中心
"""
def GetCenter():
	ComID = 0

	results = SelectCommun(ComID)
	while results:
		maxdegree = 0
		maxid = 0
		for result in results:
			if result[4] > maxdegree:
				maxdegree = result[4]
				maxid = result[0]
		print "community id  = ",ComID
		UpdateCenter(maxid)	
		ComID += 1
		results = SelectCommun(ComID)
	print "Finish Find Center"







if __name__ == "__main__":
	doGraph()
	print '===================Finish Graph======================='
	GetCenter()