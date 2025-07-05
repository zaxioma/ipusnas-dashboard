
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from textblob import TextBlob

st.set_page_config(page_title="Dashboard iPusnas", layout="wide")

st.title("📚 Dashboard Interaktif Data Peminjaman iPusnas")

uploaded_file = st.file_uploader("Unggah file JSON iPusnas", type=["json"])
if uploaded_file is not None:
    raw_json = json.load(uploaded_file)
    df = pd.json_normalize(raw_json['data'], sep='_')

    df = df[[
        'created_at',
        'sender_name',
        'book_book_title',
        'book_authors',
        'book_avg_rating',
        'total_like',
        'total_comment',
        'feed_type'
    ]]

    df['created_at'] = pd.to_datetime(df['created_at'])

    st.subheader("📈 Statistik Umum")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Jumlah Peminjaman", len(df))
    with col2:
        st.metric("Jumlah Buku Berbeda", df['book_book_title'].nunique())
    with col3:
        st.metric("Pengguna Unik", df['sender_name'].nunique())

    st.subheader("📊 Top Buku Paling Sering Dipinjam")
    top_books = df['book_book_title'].value_counts().head(10)
    st.bar_chart(top_books)

    st.subheader("🗓️ Tren Peminjaman Harian")
    daily_trend = df['created_at'].dt.hour.value_counts().sort_index()
    st.line_chart(daily_trend)

    st.subheader("⭐ Rata-rata Rating Buku")
    avg_rating = df.groupby('book_book_title')['book_avg_rating'].mean().dropna().sort_values(ascending=False).head(10)
    st.bar_chart(avg_rating)

   

    st.subheader("💬 Analisis Sentimen Komentar Pembaca")

    if 'feed_type' in df.columns and 'review_rating_comment' in df.columns:
        review_df = df[(df['feed_type'] == 'BOOK_REVIEW') & (df['review_rating_comment'].notnull())]

        if not review_df.empty:
            review_df['sentiment_polarity'] = review_df['review_rating_comment'].apply(lambda x: TextBlob(x).sentiment.polarity)
            st.write("Contoh Komentar dan Sentimennya:")
            st.dataframe(review_df[['sender_name', 'book_book_title', 'review_rating_comment', 'sentiment_polarity']].head())
    
            st.write("Distribusi Sentimen")
            st.hist_chart(review_df['sentiment_polarity'])
        else:
            st.info("Belum ada data komentar pada transaksi BOOK_REVIEW.")
    else:
        st.warning("Kolom 'feed_type' atau 'review_rating_comment' tidak ditemukan dalam data.")

    st.subheader("📬 Data Mentah")
    st.dataframe(df)
else:
    st.info("Silakan unggah file JSON terlebih dahulu.")
