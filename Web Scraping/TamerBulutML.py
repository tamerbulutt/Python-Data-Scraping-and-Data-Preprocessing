from bs4 import BeautifulSoup
import requests
import xlsxwriter
import pandas as pd
import numpy as np
import csv
#Kütüphaneler dahil edildi

#Veriyi çekeceğimiz site
siteUrl="https://www.metacritic.com/browse/movies/score/userscore/all/filtered?view=detailed&page="
detailsUrl="https://www.metacritic.com/" #detailsGenres verisini çekeceğimiz site

xlsx = xlsxwriter.Workbook('veriler1.xlsx') #Yeni bir excel oluşturuluyor
worksheet=xlsx.add_worksheet("worksheet")   #Excel'e worksheet ekleniyor
veriİslemSonrasi=xlsx.add_worksheet("veriİslemSonrası") #Excel'e diğer worksheet ekleniyor

urlPages = ["0","1","2","3","4","5"] #detailsUrl'de 6 ayrı sayfadan veri çekeceğiz döngü için lazım olacak
row=column=0 # Satır ve sütun sayımızı 0'a eşitliyoruz
row1=column1=0 #2.Döngünün satır ve sütunları

for page in urlPages:
    r=requests.get(siteUrl+page,headers={'User-agent': 'Mozilla/5.0'})#Veri için istekte bulunduk
    source = BeautifulSoup(r.content,"lxml") #BeautifulSoup kütüphanesini kullanıyoruz
    movies = source.find_all("td",attrs={"class":"clamp-summary-wrap"})#Gerekli classtan verileri buldurduk
    
    for movie in movies: #Verileri gerekli classlardan çekip değişkenlerimizin içine atıyoruz
        movieName = movie.find("a",attrs={"class":"title"}).text.lstrip().rstrip()  #FilmAdı
        movieDate = movie.find("div",attrs={"class":"clamp-details"}).findChildren()[0].text.lstrip().rstrip() #FilmTarih
        moviePoint = movie.find("div",attrs={"class":"clamp-userscore"}).findChildren()[1].text.lstrip().rstrip() #FilmPuan
        movieDetails = movie.find("a",attrs={"class":"title"},href=True) #Diğer url'e yönlendirilecek olan href burada
        r1=requests.get(detailsUrl+movieDetails["href"],headers={'User-agent': 'Mozilla/5.0'})
        source1 = BeautifulSoup(r1.content,"lxml")
        detailsGenres = source1.find("div",attrs={"class":"genres"}).findChildren()[2].text.lstrip().rstrip() #FilmKategori
        veri = [movieName,movieDate,moviePoint,detailsGenres] #Çekilen tüm verileri yeni diziye aktarıyoruz
        
        for details in veri: #Excel'in içine yazdırıyoruz
            worksheet.write(row, column, details)
            column = column+1 #Sütun 1 arttır
            
        column=0 #Sütun sıfırla
        row +=1 #Satır 1 arttır
      
        
data_xls = pd.read_excel('veriler1.xlsx', 'worksheet', index_col=0) #Excelden okuma yap
data_xls.to_csv('veriler2.csv', encoding='utf-8') #Okuduğunu csvye yaz (veri işlemeyi csvden yapacağım)

dataset = pd.read_csv('veriler2.csv') #csvden oku değişkene at
#Gerekli sütunlardan çekip değişkenlere ata
filmAd = dataset.iloc[:,0] 
filmTarih = dataset.iloc[:,1]
filmKategori = dataset.iloc[:, -1].values 
filmPuan = dataset.iloc[:, 2:3]
#OneHotEncoder için kütüphanelerin import edilmesi
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
ct = ColumnTransformer(transformers=[('encoder', OneHotEncoder(), [0])], remainder='passthrough')
filmKategori = pd.get_dummies(filmKategori) 
filmKategori = np.array(filmKategori)
filmKategori = np.array(ct.fit_transform(filmKategori), dtype = np.str)#
#Scaler için kütüphanelerin import edilmesi
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
scale = StandardScaler()
scaledFilmPuan = scale.fit_transform(filmPuan)

row1=1 #Satırı 1'e eşitle
column1=0 #Sütunu 0'a eşitle
islenmisVeri=[filmAd,filmTarih,scaledFilmPuan,filmKategori] #Değişkenleri tekrar bir diziye at
for islenmisler in islenmisVeri:
    for details in islenmisler: #Excel'in içine yazdırıyoruz          
        veriİslemSonrasi.write(row1, column1, str(details))
        row1 = row1+1
            
    row1=1
    column1 +=1

xlsx.close() #Dosyayı kapat
