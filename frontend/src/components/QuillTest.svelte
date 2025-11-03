<script lang="ts">
/**
 * QuillEditor.svelte
 * Svelte + TypeScript 변환본 (원본 JS 로직 기반)
 *
 * Props:
 *  - imageUploadUrl: string
 *  - videoUploadUrl: string
 *  - createActionUrl?: string
 *  - updateActionUrl?: string
 *  - detailBaseUrl?: string
 *  - imageMarkObserverURL?: string
 *  - imageUnmarkObserverURL?: string
 *  - videoMarkObserverURL?: string
 *  - videoUnmarkObserverURL?: string
 *  - initialContent?: string
 *  - realObjectId?: string | null
 *
 * 사용법: <QuillEditor bind:this={editorRef} imageUploadUrl="..." ... />
 */

import { onMount, onDestroy, createEventDispatcher } from 'svelte';
import type { SvelteComponent } from 'svelte';

// Try to import Quill if available as npm package; otherwise fall back to window.Quill
let Quill: any;
try {
  // prefer app-installed quill
  // @ts-ignore
  Quill = (await import('quill')).default;
} catch (err) {
  // fallback to global (CDN)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Quill = (window as any).Quill;
}

/* ---------- Props ---------- */
export let imageUploadUrl: string;
export let videoUploadUrl: string;
export let createActionUrl: string | undefined;
export let updateActionUrl: string | undefined;
export let detailBaseUrl: string | undefined;
export let imageMarkObserverURL: string | undefined;
export let imageUnmarkObserverURL: string | undefined;
export let videoMarkObserverURL: string | undefined;
export let videoUnmarkObserverURL: string | undefined;
export let initialContent: string | null = null;
export let realObjectId: string | null = null;

const dispatch = createEventDispatcher();

/* ---------- Local refs ---------- */
let editorContainer: HTMLDivElement;
let quillContainer: HTMLDivElement;
let dropArea: HTMLDivElement | null = null;
let submitForm: HTMLFormElement | null = null;
let errorTag: HTMLElement | null = null;
let submitButton: HTMLButtonElement | null = null;
let dropdownWrapper: HTMLElement | null = null;
let dropdownMenu: HTMLElement | null = null;
let dropdownToggle: HTMLElement | null = null;

/* ---------- Internal state ---------- */
let quill: any = null;
let csrfToken: string | null = null;
const headers: Record<string,string> = {};
let removedImageUrls = new Set<string>();
let removedVideoUrls = new Set<string>();

/* ---------- Type helpers ---------- */
type Nullable<T> = T | null | undefined;

/* ---------- Utilities ---------- */
function getCsrfTokenFromMeta(): string | null {
  const meta = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement | null;
  return meta?.content ?? null;
}

/* ---------- ImageResize module resolver (원본 로직 반영) ---------- */
class ImageResizeModule {
  resolveImageResize(): any | null {
    const w: any = window;
    if (typeof w.ImageResize === 'function') return w.ImageResize;
    if (w.ImageResize && typeof w.ImageResize.default === 'function') return w.ImageResize.default;
    if (w.ImageResize && typeof w.ImageResize.ImageResize === 'function') return w.ImageResize.ImageResize;
    return null;
  }
}

/* ---------- MediaGapHandler (클래스 변환, DOM 이벤트 바인딩 / unbind 제공) ---------- */
class MediaGapHandler {
  quill: any;
  options: { gapThreshold: number };
  container: HTMLElement;
  observer: MutationObserver | null = null;
  clickHandler: (e: MouseEvent) => void;

  constructor(quill: any, container: HTMLElement, options: Partial<{ gapThreshold: number }> = {}) {
    this.quill = quill;
    this.container = container;
    this.options = { gapThreshold: 25, ...options };
    this.clickHandler = this.handleClick.bind(this);
    this.initEvents();
    this.observeMutations();
  }

  initEvents() {
    this.container.addEventListener('click', this.clickHandler);
  }

  destroy() {
    this.container.removeEventListener('click', this.clickHandler);
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }

  handleClick(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (!this.container) return;
    if (!target) return;

    // 1. 미디어 클릭 시 아무 동작 안함
    const tag = target.tagName;
    if (tag === 'IMG' || tag === 'IFRAME' || tag === 'VIDEO') return;

    const rect = this.container.getBoundingClientRect();
    const clickY = e.clientY - rect.top + this.container.scrollTop;
    const children = Array.from(this.container.children) as HTMLElement[];

    for (let i = 0; i < children.length; i++) {
      const node = children[i];
      const media = this.getMedia(node);

      if (media) {
        const mediaRect = media.getBoundingClientRect();
        const mediaTop = mediaRect.top - rect.top + this.container.scrollTop;
        const mediaBottom = mediaRect.bottom - rect.top + this.container.scrollTop;

        // 위쪽 여백
        if (clickY >= mediaTop - this.options.gapThreshold && clickY <= mediaTop) {
          e.preventDefault();
          e.stopPropagation();
          this.insertParagraph(node, 'before');
          return;
        }

        // 다음 미디어와 사이에 클릭
        const nextNode = children[i + 1];
        const nextMedia = nextNode ? this.getMedia(nextNode) : null;
        if (nextMedia) {
          const nextRect = nextMedia.getBoundingClientRect();
          const nextTop = nextRect.top - rect.top + this.container.scrollTop;
          if (clickY > mediaBottom && clickY < nextTop) {
            e.preventDefault();
            e.stopPropagation();

            if (!node.nextElementSibling || node.nextElementSibling === nextNode) {
              this.insertParagraph(node, 'after');
            }
            return;
          }
        }
      }
    }
  }

  getMedia(node: Node | null): HTMLElement | null {
    if (!node || node.nodeType !== Node.ELEMENT_NODE) return null;
    const el = node as HTMLElement;
    if (el.matches && el.matches('img, iframe, video')) return el;
    return el.querySelector ? (el.querySelector('img, iframe, video') as HTMLElement | null) : null;
  }

  observeMutations() {
    this.observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of Array.from(mutation.addedNodes)) {
          const el = node as HTMLElement;
          if (!el) continue;
          if ((el.tagName === 'P' && this.getMedia(el)) || el.classList?.contains('ql-video')) {
            if (!el.nextElementSibling) {
              const newPara = document.createElement('p');
              newPara.innerHTML = '<br>';
              el.parentNode?.appendChild(newPara);
              this.scrollToElement(newPara);
            }
          }
        }
      }
    });

    this.observer.observe(this.container, { childList: true });
  }

  insertParagraph(reference: HTMLElement, position: 'before' | 'after') {
    let newPara: HTMLParagraphElement | null = null;

    if (position === 'before') {
      if (!reference.previousElementSibling || reference.previousElementSibling.textContent?.trim() !== '') {
        newPara = document.createElement('p');
        newPara.innerHTML = '<br>';
        reference.parentNode?.insertBefore(newPara, reference);
      }
    } else {
      if (!reference.nextElementSibling || reference.nextElementSibling.textContent?.trim() === '') {
        newPara = document.createElement('p');
        newPara.innerHTML = '<br>';
        reference.parentNode?.insertBefore(newPara, reference.nextSibling);
      }
    }

    if (newPara) {
      this.placeCursor(newPara);
    }
  }

  placeCursor(paragraph: HTMLElement | null) {
    if (!paragraph) return;
    const range = document.createRange();
    const sel = window.getSelection();
    range.setStart(paragraph, 0);
    range.collapse(true);
    sel?.removeAllRanges();
    sel?.addRange(range);
    this.scrollToElement(paragraph);
  }

  scrollToElement(el: Element) {
    setTimeout(() => {
      (el as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 30);
  }
}

/* ---------- QuillImageVideoHandler ---------- */
class QuillImageVideoHandler {
  quill: any;
  uploadUrl: string;
  mediaGapHandler: MediaGapHandler | null = null;

  constructor(quill: any, uploadUrl: string, mediaGapHandler?: MediaGapHandler) {
    this.quill = quill;
    this.uploadUrl = uploadUrl;
    this.mediaGapHandler = mediaGapHandler ?? null;
  }

  async uploadToServer(formFieldName: string, file: File) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000);
    const fd = new FormData();
    fd.append(formFieldName, file);

    try {
      const res = await fetch(this.uploadUrl, {
        method: 'POST',
        body: fd,
        headers,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      return await res.json();
    } catch (e) {
      clearTimeout(timeoutId);
      throw e;
    }
  }

  async imageVideoInsertHandler(file: File, type: 'image' | 'video') {
    if (!file) return;
    const isImage = file.type && file.type.startsWith('image/');

    try {
      const fieldName = isImage ? 'quillsimage' : 'quillsvideo';
      const response = await this.uploadToServer(fieldName, file);
      if (!response || !response.url) {
        throw new Error(isImage ? '이미지 업로드 실패' : '동영상 업로드 실패');
      }

      const range = this.quill.getSelection(true) || { index: this.quill.getLength(), length: 0 };
      const insertIndex = (typeof range.index === 'number') ? range.index : this.quill.getLength();
      this.quill.insertEmbed(insertIndex, type, response.url, 'user');

      // 이미지 뒤에 빈 단락 자동 추가 (원본 로직 유지)
      this.quill.insertText(insertIndex + 1, '\n', 'user');
      const newCursorIndex = insertIndex + (isImage ? 2 : 1);
      this.quill.setSelection(newCursorIndex, 0);

      const [line] = this.quill.getLine(newCursorIndex);
      const pTag = line?.domNode?.tagName?.toLowerCase() === 'p' ? line.domNode as HTMLElement : null;
      if (this.mediaGapHandler) this.mediaGapHandler.placeCursor(pTag);

    } catch (err) {
      throw err;
    }
  }
}

/* ---------- DOM Mutation Observers helpers ---------- */
function collectImgSrcsFromNode(node: Node | null): string[] {
  const urls: string[] = [];
  if (!node || node.nodeType !== Node.ELEMENT_NODE) return urls;
  const el = node as Element;
  if (el.tagName?.toUpperCase() === 'IMG') {
    const src = el.getAttribute('src');
    if (src) urls.push(src);
  }
  el.querySelectorAll?.('img').forEach(img => {
    const s = img.getAttribute('src');
    if (s) urls.push(s);
  });
  return urls;
}

function collectVideoSrcsFromNode(node: Node | null): string[] {
  const urls = new Set<string>();
  if (!(node instanceof Element)) return [];
  const el = node as Element;

  if (el.tagName?.toUpperCase() === 'IFRAME') {
    const s = el.getAttribute('src'); if (s) urls.add(s);
    el.querySelectorAll('source[src]').forEach(s => { const u = s.getAttribute('src'); if (u) urls.add(u); });
  }
  el.querySelectorAll('video[src]').forEach(v => { const s = v.getAttribute('src'); if (s) urls.add(s); });
  el.querySelectorAll('video source[src]').forEach(s => { const u = s.getAttribute('src'); if (u) urls.add(u); });
  return Array.from(urls);
}

/* ---------- Main mount ---------- */
let imageObserver: MutationObserver | null = null;
let videoObserver: MutationObserver | null = null;
let mediaGapHandlerInstance: MediaGapHandler | null = null;

onMount(() => {
  csrfToken = getCsrfTokenFromMeta();
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;

  // Ensure Quill available
  if (!Quill) {
    console.warn('Quill not found. Please install or load Quill (npm install quill or include CDN).');
    return;
  }

  // Register imageResize (if available)
  const imageResizeModule = new ImageResizeModule();
  const ImageResize = imageResizeModule.resolveImageResize();
  if (ImageResize) {
    try {
      Quill.register('modules/imageResize', ImageResize, true);
    } catch (e) {
      console.warn('imageResize register failed', e);
    }
  }
  Quill.register && Quill.register('modules/quillCustomizer', function() { /* placeholder */ });

  /* toolbar options (원본과 동일) */
  const toolbarOptions = [
    ['bold', 'italic', 'underline', 'strike'],
    ['link', 'image', 'video'],
    [{ 'header': 1 }, { 'header': 2 }, { 'header': 3 }],
    [{ 'list': 'ordered' }, { 'list': 'bullet' }, { 'list': 'check' }, { 'indent': '-1' }, { 'indent': '+1' }],
    ['blockquote', 'code-block'],
    [{ 'script': 'sub' }, { 'script': 'super' }, 'formula'],
    [{ 'color': [] }, { 'background': [] }, { 'align': ['', 'center', 'right', 'justify'] }],
  ];

  /* Quill 초기화 */
  const quillModulesConfig = {
    toolbar: {
      container: toolbarOptions,
      handlers: {
        image: () => imageInsertByToolbarButton(),
        video: () => videoInsertByToolbarButton()
      }
    },
    mediaGapHandler: { gapThreshold: 25 },
    imageResize: {
      modules: ['Resize', 'DisplaySize', 'Toolbar'],
      displayStyles: { backgroundColor: 'black', border: 'none', color: 'white' },
      handleStyles: { backgroundColor: '#fff', border: '1px solid #777', width: '10px', height: '10px' }
    }
  };

  quill = new Quill(editorContainer, {
    theme: 'snow',
    placeholder: '여기에 내용을 입력하세요...',
    modules: quillModulesConfig
  });

  // restore content
  if (initialContent) {
    try { quill.root.innerHTML = initialContent; } catch (e) { console.warn('restore failed', e); }
  }

  // 여러 DOM 참조 수집
  dropArea = document.getElementById('drop-area') as HTMLDivElement | null;
  quillContainer = document.getElementById('quill-container') as HTMLDivElement;
  submitForm = document.getElementById('submitForm') as HTMLFormElement | null;
  errorTag = document.getElementById('errorTag') as HTMLElement | null;
  submitButton = submitForm?.querySelector('[type="submit"]') as HTMLButtonElement | null;

  // MediaGapHandler 인스턴스
  mediaGapHandlerInstance = new MediaGapHandler(quill, editorContainer, { gapThreshold: 25 });

  // QuillImageVideoHandler (툴바용)
  const quillImageHandler = new QuillImageVideoHandler(quill, imageUploadUrl, mediaGapHandlerInstance);
  const quillVideoHandler = new QuillImageVideoHandler(quill, videoUploadUrl, mediaGapHandlerInstance);

  /* ---------- toolbar handlers (파일 선택) ---------- */
  function imageInsertByToolbarButton() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      try { await quillImageHandler.imageVideoInsertHandler(file, 'image'); }
      catch (err) { alert(`이미지 업로드 오류: ${err?.message || err}`); }
    };
    input.click();
  }

  function videoInsertByToolbarButton() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'video/*';
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      try { await quillVideoHandler.imageVideoInsertHandler(file, 'video'); }
      catch (err) { alert(`동영상 업로드 오류: ${err?.message || err}`); }
    };
    input.click();
  }

  /* ---------- paste (텍스트 전용 + 이미지 캡쳐 업로드) ---------- */
  const pasteHandler = (e: ClipboardEvent) => {
    if (!e.clipboardData) return;
    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    const range = quill.getSelection(true);
    quill.insertText(range.index, text, 'user');
    quill.setSelection(range.index + text.length, 0, 'user');

    const items = Array.from(e.clipboardData.items || []);
    const imageFiles = items.filter(it => it.type && it.type.indexOf('image') === 0).map(it => it.getAsFile()).filter(Boolean) as File[];
    if (imageFiles.length > 0) {
      (async () => {
        for (const file of imageFiles) {
          await quillImageHandler.imageVideoInsertHandler(file, 'image');
        }
      })();
    }
  };
  quill.root.addEventListener('paste', pasteHandler, true);

  /* ---------- drag & drop ---------- */
  if (quillContainer) {
    quillContainer.addEventListener('dragover', (ev) => { ev.preventDefault(); if (dropArea) dropArea.style.display = 'flex'; });
    quillContainer.addEventListener('dragleave', (ev) => {
      if (!quillContainer.contains(ev.relatedTarget as Node)) {
        if (dropArea) dropArea.style.display = 'none';
      }
    });
    quillContainer.addEventListener('drop', (ev) => {
      ev.preventDefault();
      ev.stopImmediatePropagation();
      if (dropArea) dropArea.style.display = 'none';
      const dt = (ev as DragEvent).dataTransfer;
      if (!dt) return;
      const files = Array.from(dt.files || []).filter(f => f.type && f.type.startsWith('image/'));
      (async () => {
        for (const file of files) {
          await quillImageHandler.imageVideoInsertHandler(file, 'image');
        }
      })();
    });
  }

  /* ---------- Image MutationObserver (삭제·undo 추적) ---------- */
  imageObserver = new MutationObserver((mutations) => {
    const toMark = new Set<string>();
    const toUnmark = new Set<string>();
    for (const m of mutations) {
      if (m.type === 'childList') {
        for (const node of Array.from(m.removedNodes)) {
          for (const url of collectImgSrcsFromNode(node)) { removedImageUrls.add(url); toMark.add(url); }
        }
        for (const node of Array.from(m.addedNodes)) {
          for (const url of collectImgSrcsFromNode(node)) {
            if (removedImageUrls.has(url)) { removedImageUrls.delete(url); toUnmark.add(url); }
          }
        }
      } else if (m.type === 'attributes' && (m as MutationRecord).attributeName === 'src') {
        const el = m.target as HTMLElement;
        if (el?.tagName?.toUpperCase() === 'IMG') {
          const oldUrl = (m as MutationRecord).oldValue || null;
          const newUrl = el.getAttribute('src') || null;
          if (oldUrl && oldUrl !== newUrl) { removedImageUrls.add(oldUrl); toMark.add(oldUrl); }
          if (newUrl && removedImageUrls.has(newUrl)) { removedImageUrls.delete(newUrl); toUnmark.add(newUrl); }
        }
      }
    }

    (async () => {
      try {
        if (toMark.size && imageMarkObserverURL) {
          await fetch(imageMarkObserverURL, { method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken ?? ''}, body: JSON.stringify(Array.from(toMark)) });
        }
        if (toUnmark.size && imageUnmarkObserverURL) {
          await fetch(imageUnmarkObserverURL, { method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken ?? ''}, body: JSON.stringify(Array.from(toUnmark)) });
        }
      } catch (err) { console.error('Image mark/unmark failed:', err); }
    })();
  });

  imageObserver.observe(editorContainer, { childList: true, subtree: true, attributes: true, attributeFilter: ['src'], attributeOldValue: true });

  /* ---------- Video MutationObserver ---------- */
  videoObserver = new MutationObserver((mutations) => {
    const toMark = new Set<string>();
    const toUnmark = new Set<string>();
    for (const m of mutations) {
      if (m.type === 'childList') {
        for (const node of Array.from(m.removedNodes)) {
          for (const url of collectVideoSrcsFromNode(node)) { removedVideoUrls.add(url); toMark.add(url); }
        }
        for (const node of Array.from(m.addedNodes)) {
          for (const url of collectVideoSrcsFromNode(node)) {
            if (removedVideoUrls.has(url)) { removedVideoUrls.delete(url); toUnmark.add(url); }
          }
        }
      } else if (m.type === 'attributes' && (m as MutationRecord).attributeName === 'src') {
        const el = m.target as HTMLElement;
        const tag = el?.tagName?.toUpperCase();
        if (tag === 'VIDEO' || tag === 'SOURCE') {
          const oldUrl = (m as any).oldValue || null;
          const newUrl = el.getAttribute('src') || null;
          if (oldUrl && oldUrl !== newUrl) { removedVideoUrls.add(oldUrl); toMark.add(oldUrl); }
          if (newUrl && removedVideoUrls.has(newUrl)) { removedVideoUrls.delete(newUrl); toUnmark.add(newUrl); }
        }
      }
    }

    (async () => {
      try {
        if (toMark.size && videoMarkObserverURL) {
          await fetch(videoMarkObserverURL, { method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken ?? ''}, body: JSON.stringify(Array.from(toMark)) });
        }
        if (toUnmark.size && videoUnmarkObserverURL) {
          await fetch(videoUnmarkObserverURL, { method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken ?? ''}, body: JSON.stringify(Array.from(toUnmark)) });
        }
      } catch (err) { console.error('Video mark/unmark failed:', err); }
    })();
  });

  videoObserver.observe(editorContainer, { childList: true, subtree: true, attributes: true, attributeFilter: ['src'], attributeOldValue: true });

  /* ---------- submit 처리 (폼이 존재할 때) ---------- */
  if (submitForm) {
    const submitListener = async (ev: Event) => {
      ev.preventDefault();
      if (!submitForm) return;
      if (submitForm.dataset.submitting === '1') return;
      submitForm.dataset.submitting = '1';
      submitButton?.setAttribute('disabled', 'true');
      if (errorTag) errorTag.textContent = '';

      try {
        const hasText = quill.getText().trim().length > 0;
        const hasImage = !!quill.root.querySelector('img');
        if (!hasText && !hasImage) throw new Error('본문을 입력해 주세요.');

        const fd = new FormData(submitForm);
        if (fd.has('content')) fd.delete('content');
        fd.append('content', quill.root.innerHTML.trim());

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 20000);

        if (realObjectId) await quillsPatch();
        else await quillsPost();
        clearTimeout(timeoutId);

        async function quillsPatch() {
          const actionUrl = submitForm?.getAttribute('action') || updateActionUrl;
          if (!actionUrl) throw new Error('업데이트 URL이 지정되지 않았습니다.');
          const res = await fetch(actionUrl, { method: 'PATCH', body: fd, headers, signal: controller.signal });
          await handleResponse(res);
        }

        async function quillsPost() {
          const actionUrl = submitForm?.getAttribute('action') || createActionUrl;
          if (!actionUrl) throw new Error('생성 URL이 지정되지 않았습니다.');
          const res = await fetch(actionUrl, { method: 'POST', body: fd, headers, signal: controller.signal });
          await handleResponse(res);
        }

        async function handleResponse(response: Response) {
          const contentType = response.headers.get('content-type') || '';
          let resObj: any = null;
          if (contentType.includes('application/json')) resObj = await response.json();
          else resObj = { message: await response.text() };

          if (!response.ok) {
            const msg = (resObj && (resObj.detail || resObj.message || resObj.error)) || `알 수 없는 오류 (HTTP ${response.status})`;
            throw new Error(msg);
          }

          if (resObj?.id) {
            window.location.href = `${detailBaseUrl}/${resObj.id}`;
            return;
          }
          if (resObj?.redirect_url) {
            window.location.href = resObj.redirect_url;
            return;
          }
          const locationHeader = response.headers.get('location');
          if (locationHeader) {
            window.location.href = locationHeader;
            return;
          }

          if (errorTag) errorTag.textContent = '저장은 되었지만, 이동할 경로를 알 수 없습니다.';
        }
      } catch (err) {
        if (`${err}` === 'Error: 본문을 입력해 주세요.') {
          if (errorTag) errorTag.innerText = '⚠️주의: 본문을 입력해 주세요.';
        } else {
          const msg = (err as any)?.name === 'AbortError' ? '요청 시간이 초과되었습니다. 네트워크 상태를 확인하고 다시 시도해 주세요.' : (err as any)?.message || String(err);
          if (errorTag) errorTag.textContent = `❌ 오류: ${msg}`;
        }
      } finally {
        if (submitForm) submitForm.dataset.submitting = '0';
        submitButton?.removeAttribute('disabled');
      }
    };

    submitForm.addEventListener('submit', submitListener);
    // store listener so we can remove later
    (submitForm as any).__submitListener = submitListener;
  }

  // dispatch ready event
  dispatch('ready', { quill });
});

/* ---------- cleanup ---------- */
onDestroy(() => {
  try {
    if (quill?.root) {
      quill.root.removeEventListener('paste', () => {});
    }
  } catch (e) { /* ignore */ }

  if (mediaGapHandlerInstance) {
    try { mediaGapHandlerInstance.destroy(); } catch (e) { /* ignore */ }
  }
  if (imageObserver) { imageObserver.disconnect(); imageObserver = null; }
  if (videoObserver) { videoObserver.disconnect(); videoObserver = null; }

  // remove submit listener if any
  try {
    const form = document.getElementById('submitForm') as HTMLFormElement | null;
    const fn = (form as any)?.__submitListener;
    if (form && fn) form.removeEventListener('submit', fn);
  } catch (e) { /* ignore */ }
});
</script>

<style>
/* 필요시 여기에 스타일 추가 */
#quill-container { min-height: 200px; }
#drop-area { display: none; justify-content:center; align-items:center; border: 2px dashed #ccc; padding: 1rem; }
.dropdown-wrapper { position: relative; }
.dropdown-wrapper .dropdown-menu { position: absolute; right: 0; top: 100%; display: none; }
.dropdown-wrapper.open .dropdown-menu { display: block; }
</style>

<div id="quill-root">
  <div id="quill-container">
    <!-- Quill이 마운트될 실제 에디터 영역 -->
    <div bind:this={editorContainer} id="editor-container"></div>
  </div>

  <!-- 드롭영역 (원본에서 사용한 element id에 맞춤) -->
  <div id="drop-area" bind:this={dropArea}>파일을 여기에 놓으세요</div>
</div>
