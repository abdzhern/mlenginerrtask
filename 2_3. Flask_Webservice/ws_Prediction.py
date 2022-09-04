#!/usr/bin/env python
# coding: utf-8

# ### 1. Import Modul

# In[1]:


import pandas as pd
import numpy as np
import tensorflow as tf



import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from sqlalchemy import create_engine

from datetime import datetime, date


# ### 2. Download data dari DB

#Fetching data iris dari database
class Load_Data:
    def get_db(self):
        try:
            con = psycopg2.connect(user="postgres",
                                  password="12345",
                                  host="127.0.0.1",
                                  port="5432",
                                  database= 'efishery')
            cur = con.cursor()


            qdataset = "SELECT sepal_length,sepal_width,petal_length,petal_width FROM iris ORDER BY id"
            qid = "SELECT id FROM iris ORDER BY id"
            cur.execute(qdataset)
            data = cur.fetchall()
            
            dataset = []
            for d in data:
                dataset.append(d)
                
            cur.execute(qid)
            ids = cur.fetchall()
            
            idlist = []
            for i in ids:
                idlist.append(i)
            
            dataset = np.asarray(dataset,dtype='float')
            idlist = np.asarray(idlist,dtype='int')

        except (Exception, psycopg2.Error) as error :
            print ("Error while fetching data from PostgreSQL", error)

        finally:
            #closing database connection.
            if(con):
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
        
        return idlist, dataset        


#Klasifikasi data iris dengan menggunakan model yang disiapkan
class Results:
    def hasil_pengolahan (self, dataset):
        
        model = tf.keras.models.load_model('ann_model.h5')
        
        # Predicting the Test set results
        y_pred = model.predict(dataset)
        y_pred = (y_pred > 0.5)

        prediction=model.predict(dataset)
        predict_label=np.argmax(prediction,axis=1)
        
        label = predict_label.tolist()
        
        return label

def addapt_numpy_int32(numpy_int32):
    return AsIs(numpy_int32)    


#simpan hasil klasifikasi ke dalam db
class Save:
    def simpan_data (self, idlist, label):

        register_adapter(np.int32, addapt_numpy_int32)

        id_list = [item for sublist in idlist for item in sublist]

        dt_time = datetime.now()
        dt_date = date.today()

        values = [] 
        for i in range (0, len(label)):
            values.append((
                dt_date,
                dt_time,
                id_list[i],
                label[i]
                )) #append data
        
        try:
            con = psycopg2.connect(user="postgres",
                                  password="12345",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="efishery")

            cur = con.cursor()
                        
            q = """ INSERT INTO hasil (
                    tanggal,waktu,id_iris,class ) 
                    VALUES (%s,%s,%s,%s)           
                """
            # save table prediksi ke db
            cur.executemany(q,values)

            # Make the changes to the database persistant
            con.commit()


        except (Exception, psycopg2.Error) as error :
            print ("Error while saving data from PostgreSQL", error)

        finally:
            #closing database connection.
            if(con):
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")



