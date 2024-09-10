from pytrends.request import TrendReq

# Google Trends verilerini çekme fonksiyonu
def get_trends_data(keyword, geo=''):
    try:
        # Google Trends API'yi başlat
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Anahtar kelime ve lokasyonla ilgili veri yükle
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo=geo, gprop='')
        
        # Zamanla ilgi gösterimi verilerini al
        data = pytrends.interest_over_time()
        
        # Eğer veri varsa, JSON formatında döndür
        if not data.empty:
            return data[keyword].to_json()
        else:
            return "No data found for the keyword."

    except Exception as e:
        return f"Error occurred: {str(e)}"

# Google Trends'ten ilgili anahtar kelimenin daha fazla metrik verisini alma fonksiyonu
def get_trends_related_queries(keyword, geo=''):
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo=geo, gprop='')
        
        # İlgili aramaları alma
        related_queries = pytrends.related_queries()
        
        if related_queries:
            return related_queries[keyword]['top'].to_json()  # 'top' yerine 'rising' kullanılabilir
        else:
            return "No related queries found."

    except Exception as e:
        return f"Error occurred: {str(e)}"
