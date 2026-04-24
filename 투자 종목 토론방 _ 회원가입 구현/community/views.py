from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from .utils import load_assets, get_asset_by_id
from .models import Comment, Post
# from .llm import is_inappropriate  # [심화] LLM 부적절 댓글 필터링


def asset_list(request):
    """금융 자산 리스트 (JSON에서 로드)"""
    assets = load_assets()
    context = {"assets": assets}
    return render(request, "community/asset_list.html", context)


def board(request, asset_id):
    """해당 자산의 토론 게시판 (게시글 목록)"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    posts = Post.objects.filter(asset_id=asset_id)
    context = {"asset": asset, "posts": posts}
    return render(request, "community/board.html", context)


def post_detail(request, asset_id, post_id):
    """게시글 상세"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    comments = post.comments.all()
    can_edit = request.user.is_authenticated and post.author == request.user.username
    context = {"asset": asset, "post": post, "comments": comments, "can_edit": can_edit}
    return render(request, "community/post_detail.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def post_create(request, asset_id):
    """게시글 작성"""  # (제목·내용 LLM 부적절 검사 주석 처리)
    asset = get_asset_by_id(asset_id)

    if not asset:
        return render(request, "community/404.html", status=404)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if title and content:
            # [심화] LLM 부적절 댓글 필터링
            # if is_inappropriate(title) or is_inappropriate(content):
            #     messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 등록해 주세요.")
            #     context = {"asset": asset, "title": title, "content": content, "author": author}
            #     return render(request, "community/post_form.html", context)

            Post.objects.create(
                asset_id=asset_id,
                title=title,
                content=content,
                author=request.user.username,
            )
            return redirect("community:board", asset_id=asset_id)
    context = {"asset": asset}
    return render(request, "community/post_form.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def post_update(request, asset_id, post_id):
    """게시글 수정"""  # (제목·내용 LLM 부적절 검사 주석 처리)
    asset = get_asset_by_id(asset_id)

    if not asset:
        return render(request, "community/404.html", status=404)
        
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    if post.author != request.user.username:
        messages.error(request, "본인이 작성한 게시글만 수정할 수 있습니다.")
        return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        if title and content:
            # [심화] LLM 부적절 댓글 필터링
            # if is_inappropriate(title) or is_inappropriate(content):
            #     messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 저장해 주세요.")
            #     context = {
            #         "asset": asset,
            #         "post": post,
            #         "title": title,
            #         "content": content,
            #         "author": author,
            #         "is_edit": True,
            #     }
            #     return render(request, "community/post_form.html", context)
            
            post.title = title
            post.content = content
            post.save()
            return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)

    # GET 요청 또는 유효성 실패 시 기존 값 채워서 폼 렌더링
    context = {
        "asset": asset,
        "post": post,
        "title": post.title,
        "content": post.content,
        "is_edit": True,
    }
    return render(request, "community/post_form.html", context)


@require_http_methods(["POST"])
@login_required
def post_delete(request, asset_id, post_id):
    """게시글 삭제"""
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    if post.author != request.user.username:
        messages.error(request, "본인이 작성한 게시글만 삭제할 수 있습니다.")
        return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)
    post.delete()
    messages.success(request, "게시글이 삭제되었습니다.")
    return redirect("community:board", asset_id=asset_id)


@require_http_methods(["POST"])
@login_required
def comment_create(request, asset_id, post_id):
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    content = request.POST.get("content", "").strip()
    if content:
        Comment.objects.create(post=post, author=request.user.username, content=content)
        messages.success(request, "댓글이 등록되었습니다.")
    else:
        messages.error(request, "댓글 내용을 입력해 주세요.")
    return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)


@require_http_methods(["POST"])
@login_required
def comment_delete(request, asset_id, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id, post__asset_id=asset_id)
    if comment.author != request.user.username:
        messages.error(request, "본인이 작성한 댓글만 삭제할 수 있습니다.")
        return redirect("community:post_detail", asset_id=asset_id, post_id=post_id)
    comment.delete()
    messages.success(request, "댓글이 삭제되었습니다.")
    return redirect("community:post_detail", asset_id=asset_id, post_id=post_id)
