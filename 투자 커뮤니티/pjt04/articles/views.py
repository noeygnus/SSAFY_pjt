import json
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Article

def load_assets():
    json_path = Path(settings.BASE_DIR) / 'data' / 'assets.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def index(request):
    assets_data = load_assets()
    return render(request, 'articles/index.html', {'assets_data': assets_data})

def asset_board(request, asset_id):
    assets = load_assets()
    asset = next((a for a in assets if str(a['id']) == asset_id), None)
    if asset is None:
        return render(request, '404.html', status=404)
    articles = Article.objects.filter(asset_id=asset_id).order_by('-created_at')
    return render(request, 'articles/asset_board.html', {'asset': asset, 'articles': articles})

def create(request, asset_id):
    assets = load_assets()
    asset = next((a for a in assets if str(a['id']) == asset_id), None)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author') or "익명"
        if title and content:
            Article.objects.create(asset_id=asset_id, title=title, content=content, author=author)
            return redirect('articles:asset_board', asset_id=asset_id)
    return render(request, 'articles/create.html', {'asset': asset})

def detail(request, asset_id, article_pk):
    article = get_object_or_404(Article, pk=article_pk, asset_id=asset_id)
    assets = load_assets()
    asset = next((a for a in assets if str(a['id']) == asset_id), None)
    return render(request, 'articles/detail.html', {'article': article, 'asset': asset})

def update(request, asset_id, article_pk):
    article = get_object_or_404(Article, pk=article_pk, asset_id=asset_id)
    assets = load_assets()
    asset = next((a for a in assets if str(a['id']) == asset_id), None)
    if request.method == 'POST':
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        article.author = request.POST.get('author') or "익명"
        article.save()
        return redirect('articles:detail', asset_id=asset_id, article_pk=article_pk)
    return render(request, 'articles/update.html', {'article': article, 'asset': asset})

def delete(request, asset_id, article_pk):
    article = get_object_or_404(Article, pk=article_pk, asset_id=asset_id)
    if request.method == 'POST':
        article.delete()
    return redirect('articles:asset_board', asset_id=asset_id)