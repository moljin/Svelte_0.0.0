<script>
    import {onMount, onDestroy} from 'svelte';
    import Quill from 'quill';
    import 'quill/dist/quill.snow.css'; // Quill 스노우 테마 CSS

    // 부모가 넘겨줄 콜백
    export let onContentChange = (html) => {
    };

    // FIX: 외부에서 초기 내용을 받을 경우 prop으로 선언
    export let content = '';

    let quill;
    let editorContainer; // 에디터가 렌더링될 DOM 요소

    // Svelte store 또는 prop을 통해 외부에서 content 값을 받아올 경우 사용
    // export let content = '';
    // 내부 업데이트 중임을 표시(외부 -> 내부 반영 시 change 루프 방지)
    let internalPatching = false;


    onMount(() => {
        const toolbarOptions = [
            ['bold', 'italic', 'underline', 'strike'],        // 텍스트 스타일
            ['blockquote', 'code-block'],

            [{'header': 1}, {'header': 2}],               // 제목 크기
            [{'list': 'ordered'}, {'list': 'bullet'}],
            [{'script': 'sub'}, {'script': 'super'}],      // 첨자/위첨자
            [{'indent': '-1'}, {'indent': '+1'}],          // 들여쓰기/내어쓰기
            [{'direction': 'rtl'}],                         // 텍스트 방향

            [{'size': ['small', false, 'large', 'huge']}],  // 폰트 크기
            [{'header': [1, 2, 3, 4, 5, 6, false]}],

            [{'color': []}, {'background': []}],          // 폰트 색상/배경 색상
            [{'font': []}],

            [{'align': []}],                                // 텍스트 정렬

            ['clean']                                         // 포맷 제거
        ];

        quill = new Quill(editorContainer, {
            modules: {
                toolbar: toolbarOptions
            },
            theme: 'snow' // 스노우 테마 사용
        });

        // 초기 내용 반영
        if (content && content.trim().length > 0) {
            internalPatching = true;
            const sel = quill.getSelection();
            quill.clipboard.dangerouslyPasteHTML(0, content, 'api');
            if (sel) quill.setSelection(sel);
            internalPatching = false;
        }


        // 에디터 내용이 변경될 때마다 부모 컴포넌트로 이벤트를 디스패치
        quill.on('text-change', () => {
            // HTML 내용을 부모 컴포넌트로 전달
            if (internalPatching) return;

            const html = quill.root.innerHTML;
            onContentChange?.(html);

        });

        // 초기 렌더 직후 현재 내용을 한 번 전달하고 싶다면 주석 해제
        // onContentChange?.(quill.root.innerHTML);

    });

    // 외부에서 content가 변경되면 에디터에 반영
    $: if (quill) {
        const current = quill.root?.innerHTML ?? '';
        const next = content ?? '';
        if (!internalPatching && next !== current) {
            internalPatching = true;
            const sel = quill.getSelection();
            quill.clipboard.dangerouslyPasteHTML(0, next, 'api');
            if (sel) quill.setSelection(sel);
            internalPatching = false;
        }
    }


    onDestroy(() => {
        if (quill) {
            quill = null;
        }
    });
</script>

<!-- Quill 에디터가 마운트될 DIV -->
<!--<div bind:this={editorContainer}></div>-->
<div bind:this={editorContainer} id="quill-editor" class="quill-editor"></div>


<style>
    /* Quill 에디터 높이 설정 */
    #quill-editor {
            border-radius: 0 0 10px 10px;
            height: auto;
            min-height: 300px;
            overflow: auto;
            font-size: 16px; /*detail page와 동일하게 맞춤 (글씨 크기, 줄간격, 단락 간격(margin-top, margin-bottom))*/
        }
    /*:global(.ql-editor) {*/
    /*    min-height: 200px;*/
    /*}*/
</style>
