<script>
    import { push } from 'svelte-spa-router'
    import fastapi from "../lib/api"
    import Error from "../components/Error.svelte"
    // QuillEditor 컴포넌트 경로 확인 (프로젝트 구조에 맞게 수정)
    import QuillEditor from '../components/QuillEditor.svelte';

    let error = {detail:[]}
    let subject = ''
    let content = '' // Quill 에디터의 HTML 내용이 저장될 변수

    // Quill 에디터에서 내용 변경 이벤트 발생 시 호출될 함수
    function handleContentChange(html) {
        content = html;

    // function handleContentChange(event) {
        // content = event.detail; // 에디터의 HTML 내용을 content 변수에 저장
        console.log("content:", content);
    }

    function post_question(event) {
        event.preventDefault()
        let url = "/apis/questions/post"
        let params = {
            subject: subject,
            content: content, // HTML 내용이 포함된 content 변수 전송
        }
        fastapi('post', url, params,
            (json) => {
                push("/")
            },
            (json_error) => {
                error = json_error
            }
        )
    }
</script>

<div class="container">
    <h5 class="my-3 border-bottom pb-2">질문 등록</h5>
    <Error error={error} />
    <form id="submitForm" method="post" class="my-3">
        <div class="mb-3">
            <label for="subject">제목</label>
            <input type="text" class="form-control" bind:value="{subject}">
        </div>
        <div class="mb-3">
            <label for="content">내용</label>
            <!-- 기존 textarea는 제거하거나 주석 처리 -->
            <!-- <textarea class="form-control" rows="10" bind:value="{content}"></textarea> -->
            <hr>
            <!-- Quill 에디터 컴포넌트 사용 및 이벤트 핸들러 바인딩 -->
            <div id="quill-container" class="">
                <!-- QuillEditor 컴포넌트에서 contentChange 이벤트 발생 시 handleContentChange 함수 실행 -->
                <QuillEditor onContentChange={handleContentChange} />
            </div>
        </div>

        <div class="text-end">
            <button type="submit" class="btn btn-primary" on:click="{post_question}">저장하기</button>
        </div>
    </form>
</div>

