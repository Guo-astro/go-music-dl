//go:build android

package main

import (
	"log"

	"gioui.org/app"
	"git.wow.st/gmp/jni"
)

func (a *desktopApp) requestAndroidWebViewFocus(evt app.ViewEvent) {
	if a.androidWebViewFocusOnce {
		return
	}
	androidEvt, ok := evt.(app.AndroidViewEvent)
	if !ok || androidEvt.View == 0 {
		return
	}

	a.androidWebViewFocusOnce = true
	view := jni.Object(androidEvt.View)
	go a.window.Run(func() {
		if err := requestAndroidWebViewFocusFromView(view); err != nil {
			log.Printf("request Android WebView focus: %v", err)
		}
	})
}

func requestAndroidWebViewFocusFromView(view jni.Object) error {
	return jni.Do(jni.JVMFor(app.JavaVM()), func(env jni.Env) error {
		className := jni.FindClass(env, "org/gioui/MusicDLWebViewSupport")
		method := jni.GetStaticMethodID(env, className, "focusWebViewWhenReady", "(Landroid/view/View;)V")
		return jni.CallStaticVoidMethod(env, className, method, jni.Value(view))
	})
}
