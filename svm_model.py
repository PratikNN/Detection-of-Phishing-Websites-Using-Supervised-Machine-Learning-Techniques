#!/usr/bin/env python
# coding: utf-8

# # SVM Model

# In[15]:


from sklearn.svm import SVC
import numpy as np
import pandas as pd
import keras
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import pickle as pkl


# In[16]:


data = pd.read_csv('PhisingWebsite_datset.csv')


# In[17]:


def prepare_data(data):
    y = data['Result']
    x = data.drop('Result',axis =1)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size= 0.3, random_state=42)
    return x_train, x_test, y_train, y_test


# In[18]:


x_train, x_test, y_train, y_test = prepare_data(data=data)


# In[19]:


svm=SVC(kernel='rbf')
svm.fit(x_train,y_train)
y_svm_pred=svm.predict(x_test)


# In[20]:


with open("SVM",'wb') as f:
    pkl.dump(svm,f)


# In[21]:


svm_acc=accuracy_score(y_true=y_test,y_pred=y_svm_pred)
print("Overall Accuracy of SVM model using test-set is:%f"%(svm_acc*100))


# In[ ]:




