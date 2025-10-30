// - 프로젝트 루트(package.json이 있는 폴더)에 .jshintrc 생성
/* 아래를 작성
{
  "esversion": 11,
  "module": true,
  "browser": true,
  "sub": true,
  "undef": true,

  "globals": {
    "alert": true,
    "fetch": true,
    "URLSearchParams": true
  }
}
*/
// PyCharm 설정: Settings > Languages & Frameworks > JavaScript > Code Quality Tools > JSHint에서
// Use config file 을 체크한다.

import qs from "qs";
import { access_token, username, is_login } from "./store";
import { get } from 'svelte/store';
import { push } from 'svelte-spa-router';

const fastapi = (operation, url, params, success_callback, failure_callback) => {
    let method = operation;
    let content_type = 'application/json';
    let body = JSON.stringify(params);

    if(operation === 'login') {
        method = 'post';
        content_type = 'application/x-www-form-urlencoded';
        body = qs.stringify(params);
    }

    let _url = import.meta.env.VITE_SERVER_URL+url;

    if(method === 'get') {
        _url += "?" + new URLSearchParams(params);
    }

    let options = {
        method: method,
        headers: {
            "Content-Type": content_type
        }
    };

    const _access_token = get(access_token);
    if (_access_token) {
        options.headers["Authorization"] = "Bearer " + _access_token;
    }

    if (method !== 'get') {
        options['body'] = body;
    }

    fetch(_url, options)
        .then(response => {
            if(response.status === 204) {  // No content
                if(success_callback) {
                    success_callback();
                }
                return;
            }
            response.json()
                .then(json => {
                    if(response.status >= 200 && response.status < 300) {  // 200 ~ 299
                        if (success_callback) {
                            success_callback(json);
                        }
                    } else if (operation !== 'login' && response.status === 401) { // token time out
                        access_token.set('');
                        username.set('');
                        is_login.set(false);
                        alert("로그인이 필요합니다.");
                        void push('/user-login');
                    } else {
                        if (failure_callback) {
                            failure_callback(json);
                        }else {
                            alert(json.detail);
                            // alert(JSON.stringify(json));
                        }
                    }
                })
                .catch(error => {
                    alert(JSON.stringify(error));
                });
        });
};

export default fastapi;
