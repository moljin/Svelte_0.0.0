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

    // 내부 업데이트 중임을 표시(외부 -> 내부 반영 시 change 루프 방지)
    let internalPatching = false;

    // ADD: responsive toolbar enhancer
    function makeToolbarResponsive(quill, config) {
        const toolbar = quill.getModule('toolbar')?.container;
        if (!toolbar) return () => {};
        if (toolbar.dataset.responsive === '1') return () => {};
        toolbar.dataset.responsive = '1';

        // Capture original groups before restructuring
        const groups = Array.from(toolbar.querySelectorAll(':scope > .ql-formats'));
        const total = groups.length;

        // Build wrappers inside the same toolbar container
        const main = document.createElement('div');
        main.className = 'ql-toolbar-main';

        const moreWrap = document.createElement('div');
        moreWrap.className = 'ql-toolbar-more';

        const moreBtn = document.createElement('button');
        moreBtn.type = 'button';
        moreBtn.className = 'ql-more-btn';
        moreBtn.setAttribute('aria-haspopup', 'true');
        moreBtn.setAttribute('aria-expanded', 'false');
        moreBtn.title = 'More';
        moreBtn.innerHTML = '⋯';

        const menu = document.createElement('div');
        menu.className = 'ql-more-menu';
        menu.setAttribute('role', 'menu');
        menu.hidden = true;

        moreWrap.appendChild(moreBtn);
        moreWrap.appendChild(menu);

        // Replace toolbar content with wrappers and put groups into "main" initially
        toolbar.innerHTML = '';
        toolbar.appendChild(main);
        toolbar.appendChild(moreWrap);
        groups.forEach((g) => main.appendChild(g));

        // Sort steps by maxWidth ascending
        const steps = (config?.steps ?? []).slice().sort((a, b) => a.maxWidth - b.maxWidth);

        function visibleFor(width) {
            for (const s of steps) {
                if (width <= s.maxWidth) return Math.min(s.visible, total);
            }
            return total;
        }

        function layout() {
            const visible = visibleFor(window.innerWidth);

            // Move groups according to computed visible count
            main.innerHTML = '';
            menu.innerHTML = '';

            groups.forEach((g, idx) => {
                if (idx < visible) main.appendChild(g);
                else menu.appendChild(g);
            });

            const hasOverflow = menu.childElementCount > 0;
            moreWrap.style.display = hasOverflow ? '' : 'none';
            if (!hasOverflow) {
                moreBtn.setAttribute('aria-expanded', 'false');
                menu.hidden = true;
            }
        }

        const relayout = (() => {
            let raf = 0;
            return () => {
                cancelAnimationFrame(raf);
                raf = requestAnimationFrame(layout);
            };
        })();

        function toggleMenu(e) {
            e?.preventDefault();
            const open = menu.hidden;
            menu.hidden = !open;
            moreBtn.setAttribute('aria-expanded', String(open));
        }

        function handleOutsideClick(e) {
            if (!menu.hidden && !moreWrap.contains(e.target)) {
                menu.hidden = true;
                moreBtn.setAttribute('aria-expanded', 'false');
            }
        }

        moreBtn.addEventListener('click', toggleMenu);
        window.addEventListener('resize', relayout);
        document.addEventListener('click', handleOutsideClick);

        // Initial layout
        layout();

        // Cleanup
        return () => {
            moreBtn.removeEventListener('click', toggleMenu);
            window.removeEventListener('resize', relayout);
            document.removeEventListener('click', handleOutsideClick);
            toolbar.removeAttribute('data-responsive');
        };
    }

    let teardownToolbar;



    onMount(() => {
        const toolbarOptions = [
            ['bold', 'italic', 'underline', 'strike'],        // 텍스트 스타일
            ['link', 'image', 'video'],
            [{'header': 1}, {'header': 2}, {'header': 3}],               // 제목 크기

            [{'list': 'ordered'}, {'list': 'bullet'}, {'list': 'check'}, {'indent': '-1'}, {'indent': '+1'}],
            [{'color': []}, {'background': []}, {'align': []}],          // 폰트 색상/배경 색상
            ['blockquote', 'code-block'],
            [{'script': 'sub'}, {'script': 'super'}],          // 들여쓰기/내어쓰기
            [{'direction': 'rtl'}],                         // 텍스트 방향

            // [{'size': ['small', false, 'large', 'huge']}],  // 폰트 크기
            // [{'header': [1, 2, 3, 4, 5, 6, false]}],


            // [{'font': []}],

            // [{'align': []}],                                // 텍스트 정렬

            // ['clean']                                         // 포맷 제거
        ];

        quill = new Quill(editorContainer, {
            modules: {
                toolbar: toolbarOptions
            },
            theme: 'snow' // 스노우 테마 사용
        });

        // 게시글 수정 화면에서 저장되어 있던 내용(content) 반영
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

        // ADD: enable responsive toolbar at the requested breakpoints
        teardownToolbar = makeToolbarResponsive(quill, {
            steps: [
                // width <= maxWidth -> keep "visible" groups on the main bar
                { maxWidth: 510, visible: 2 },
                { maxWidth: 710, visible: 3 },
                { maxWidth: 770, visible: 3 },
                { maxWidth: 995, visible: 4 },
                { maxWidth: 1030, visible: 6 },
                { maxWidth: Infinity, visible: 999 } // wide screens show all
            ]
        });


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
        // if (quill) {
        //     quill = null;
        // }
        teardownToolbar?.();

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
    :global(.ql-editor) {
       line-height: 1.8;
    }
    /* Minimal styling for the responsive toolbar wrappers */
    /* 기존: height: 50px; => 드롭다운이 가려질 수 있음 */
    :global(.ql-toolbar) {
        height: auto; /* 고정 높이 제거 */
        min-height: 55px; /* 필요 시 최소 높이만 유지 */
        border-radius: 10px 10px 0 0;
    }

    :global(.ql-toolbar.ql-snow) {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: nowrap;
        position: relative; /* 드롭다운의 스택 컨텍스트 보강 */
        z-index: 1; /* 드롭다운의 스택 컨텍스트 보강 */

    }
    :global(.ql-toolbar.ql-snow .ql-formats) {
        margin-right: 8px;
    }
    :global(.ql-snow .ql-picker.ql-expanded .ql-picker-options) {
        top: 105%;
    }

    :global(.ql-toolbar .ql-toolbar-main) {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1 1 auto;
        flex-wrap: nowrap;
        overflow: visible;
        /*overflow: hidden; !* keep main row single-line *!*/
    }

    :global(.ql-toolbar .ql-toolbar-more) {
        position: relative;
        flex: 0 0 auto;
    }

    :global(.ql-toolbar .ql-more-btn) {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border: 1px solid var(--ql-border-color, #ccc);
        background: #fff;
        border-radius: 4px;
        cursor: pointer;
        font-size: 18px;
        line-height: 1;
        padding: 0;
    }

    :global(.ql-toolbar .ql-more-menu) {
        position: absolute;
        right: 0;
        top: calc(100% + 6px);
        background: #fff;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 8px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        z-index: 1000;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
        min-width: 240px;
        max-width: 80vw;
        overflow: visible; /* 내부 피커가 더 커져도 보이도록 */
    }

    /* Quill 드롭다운이 다른 요소 위로 확실히 올라오게 */
    :global(.ql-toolbar .ql-picker.ql-expanded .ql-picker-options) {
        z-index: 2000;
    }

    /* Optional: tighten spacing for groups inside dropdown */
    :global(.ql-toolbar .ql-more-menu .ql-formats) {
        margin: 0;
    }

    /* 툴바 아이콘 SVG 한 단계(20%) 확대 */
  :global(.ql-toolbar.ql-snow .ql-formats button svg),
  :global(.ql-toolbar.ql-snow .ql-picker-label svg),
  :global(.ql-toolbar.ql-snow .ql-picker-item svg) {
    transform: scale(1.3);
    transform-origin: center;
  }

  /* 확대 시 아이콘이 잘리지 않도록 */
  :global(.ql-toolbar.ql-snow .ql-formats button),
  :global(.ql-toolbar.ql-snow .ql-picker-label) {
    overflow: visible;
  }

  :global(.ql-snow .ql-stroke) {stroke-width: 1.5;}
    :global(button.ql-strike > svg > path),
    :global(button.ql-header > svg > path),
    :global(button.ql-script > svg > path)  {stroke:white; stroke-width: 0.5}
    :global(.ql-toolbar-more button) {font-size: 25px !important;}
    :global(.ql-toolbar-main > span:nth-child(2)) {display: flex; gap: 5px;}
    :global(.ql-toolbar-main > span:nth-child(3)) {display: flex; gap: 5px;}
    :global(.ql-toolbar-main > span:nth-child(4)) {display: flex; gap: 5px;}
    :global(.ql-toolbar-main > span:nth-child(5)) {display: flex; gap: 5px;}
    :global(.ql-toolbar-main > span:nth-child(6)) {display: flex; gap: 5px;}
    :global(.ql-toolbar-main > span:nth-child(8)) {display: flex; gap: 5px;}

</style>
