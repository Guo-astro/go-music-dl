package org.gioui;

import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;

public final class MusicDLWebViewSupport {
    private static final int MAX_FOCUS_ATTEMPTS = 24;
    private static final long FOCUS_RETRY_DELAY_MS = 250;

    private MusicDLWebViewSupport() {}

    public static void focusWebViewWhenReady(View root) {
        focusWebViewWhenReady(root, MAX_FOCUS_ATTEMPTS);
    }

    private static void focusWebViewWhenReady(final View root, final int attemptsLeft) {
        WebView webView = findWebView(root);
        if (webView != null) {
            webView.setFocusable(true);
            webView.setFocusableInTouchMode(true);
            if (webView.requestFocus()) {
                return;
            }
        }
        if (attemptsLeft <= 0) {
            return;
        }
        root.postDelayed(new Runnable() {
            @Override
            public void run() {
                focusWebViewWhenReady(root, attemptsLeft - 1);
            }
        }, FOCUS_RETRY_DELAY_MS);
    }

    private static WebView findWebView(View view) {
        if (view instanceof WebView) {
            return (WebView) view;
        }
        if (!(view instanceof ViewGroup)) {
            return null;
        }
        ViewGroup group = (ViewGroup) view;
        for (int index = 0; index < group.getChildCount(); index++) {
            WebView match = findWebView(group.getChildAt(index));
            if (match != null) {
                return match;
            }
        }
        return null;
    }
}
