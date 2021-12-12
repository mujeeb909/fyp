import os

from django.shortcuts import render, redirect
import pickle
from django.contrib import messages
from .forms import *
from store.models import products
from .models import *
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Create your views here.
def Itemreview(request, id):
    item = products.objects.get(id=id)
    
    text = None
    result = ""
    form = reviewform()
    if request.method == 'POST':
        form = reviewform(request.POST)
        if form.is_valid():
            review = form.cleaned_data['review']
            rate = form.save(commit=False)
            rate.user = request.user
            rate.item = item
            sid_obj = SentimentIntensityAnalyzer()
            sentiment_dict = sid_obj.polarity_scores(review)
            if sentiment_dict['compound'] >= 0.05 :
	             result = "Positive"
            elif sentiment_dict['compound'] <= - 0.05 :
	            result = "Negative"
            else :
	            result = "Neutral"
           
            rate.review_predict = result
            rate.review = review
            rate.save()
            messages.success(request, 'Rating added successfully')
            return redirect('/profile/%d/' % request.user.id)
        else:
            form = reviewform()

    context = {
        'form': form,
    }
    return render(request, 'review.html', context)