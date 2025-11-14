// scripts.js
document.addEventListener('DOMContentLoaded', () => {
    const commentsContainer = document.getElementById('comments');
    const commentForm = document.getElementById('comment-form');
    const commentContent = document.getElementById('comment-content');

    function fetchComments() {
        fetch('/api/comments')
            .then(response => response.json())
            .then(comments => {
                commentsContainer.innerHTML = '';
                comments.forEach(comment => renderComment(comment));
            });
    }

    function renderComment(comment, isReply = false) {
        const commentElement = document.createElement('div');
        commentElement.classList.add('comment');
        if (isReply) {
            commentElement.classList.add('reply');
        }

        commentElement.innerHTML = `
            <p><strong>${comment.username}</strong>: ${comment.content}</p>
            <button onclick="deleteComment(${comment.id})">删除</button>
            <button onclick="showReplyForm(${comment.id})">回复</button>
            <div id="reply-form-${comment.id}" style="display: none;">
                <form onsubmit="addReply(event, ${comment.id})">
                    <textarea id="reply-content-${comment.id}" placeholder="输入你的回复..."></textarea>
                    <button type="submit">回复</button>
                </form>
            </div>
            <div id="replies-${comment.id}"></div>
        `;

        if (comment.replies.length > 0) {
            comment.replies.forEach(reply => renderComment(reply, true));
        }

        commentsContainer.appendChild(commentElement);
    }

    function addComment(event) {
        event.preventDefault();
        const content = commentContent.value.trim();
        if (content === '') return;

        fetch('/api/comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        })
        .then(response => response.json())
        .then(comment => {
            renderComment(comment);
            commentContent.value = '';
        });
    }

    function addReply(event, parentId) {
        event.preventDefault();
        const replyContent = document.getElementById(`reply-content-${parentId}`).value.trim();
        if (replyContent === '') return;

        fetch('/api/comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: replyContent, parent_id: parentId })
        })
        .then(response => response.json())
        .then(reply => {
            const repliesContainer = document.getElementById(`replies-${parentId}`);
            renderComment(reply, true);
            document.getElementById(`reply-content-${parentId}`).value = '';
        });
    }

    function deleteComment(commentId) {
        fetch(`/api/comments/${commentId}`, {
            method: 'DELETE'
        })
        .then(() => {
            const commentElement = document.querySelector(`.comment[id="${commentId}"]`);
            if (commentElement) {
                commentElement.remove();
            }
        });
    }

    function showReplyForm(commentId) {
        const replyForm = document.getElementById(`reply-form-${commentId}`);
        if (replyForm.style.display === 'none') {
            replyForm.style.display = 'block';
        } else {
            replyForm.style.display = 'none';
        }
    }

    commentForm.addEventListener('submit', addComment);

    fetchComments();
});
