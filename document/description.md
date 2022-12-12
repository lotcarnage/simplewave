# simplewave

## はじめに

本モジュールはWaveファイルを簡単な手続きで読み書きできるようにするためのモジュールです。

## インストール方法

```
pip install simplewave
```

## コマンド実行

インストールすると`fetchwave`コマンドを使えるようになります。
`fetchwave`コマンドは第一引数に Wave ファイルへのパスをとり、
指定された Wave ファイルのヘッダ情報を読み込んで表示します。

## ライブラリとしての使い方

### Wave ファイル読み込み

```python
import simplewave

pcms, Fs, nch = simplewave.load('test.wav')
```

### Wave ファイル書き込み

```python
import simplewave

simplewave.save('output.wav', pcms, Fs)
```

## 備考

### 互換性

本モジュールは開発版のため、バージョン更新により仕様が変わる可能性があります。

以上
