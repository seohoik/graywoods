---
title: 'Drafts 개발자가 만든 사전: Terminology'
categories:
  - apps
tags:
  - app
  - ipad
  - iphone
  - 사전
pubDate: 2016-04-17
description: 기본 설명을 입력하세요
---

아이폰이나 아이프드에서 사전 앱을 많이 사용하시나요? 전 이제 학생도 아니고 영어로된 텍스트를 읽을 일도 그렇게 많지 않다보니까 사전을 자주 사용하지는 않습니다. 그래서 이런저런 좋은 사전이 새로 나오거나 가끔 무료로 풀려도 몇 번 사용해보고는 늘 쓰던 사전으로 돌아옵니다. 바로 그 늘 돌아오는 사전이 [Terminology](https://itunes.apple.com/us/app/terminology-3-extensible-dictionary/id687798859?mt=8)입니다.

이 앱은 [Drafts](https://itunes.apple.com/us/app/drafts-4-quickly-capture-notes/id905337691?mt=8)를 만든 [Agile Tortoise](http://agiletortoise.com/)에서 만든 사전 앱입니다. Drafts를 사용해 봤다면 잘 아시겠지만 이 앱도 url scheme를 기반으로 작동하도록 되어 있어서 이를 지원하는 사전앱이 여러 개 있다면 먼저 찾고 싶은 단어를 쓴 다음에 취향에 맞는 사전을 이것저것 골라서 단어를 검색해 볼 수 있는 장점이 있습니다.

그리고 네이버 사전처럼 웹을 지원하는 사전이 있다면 웹에서 바로 검색을 할 수도 있어서 여러모로 편리합니다. 웹 기반의 사전용 액션은 간단하게 만들 수 있습니다. 예를 들어, 네이버 사전에 접속해서 특정 단어를 검색한 다음에 그 단어 부분만 \[\[term\]\]으로 바꿔 주시면 됩니다.

개인적으로 매우 유용하다고 생각하는 검색 명령 한 가지는 아래의 것입니다.

```
http://www.lextutor.ca/cgi-bin/conc/wwwassocwords.pl?lingo=English&amp;KeyWordFormat=&amp;Maximum=999&amp;LineWidth=120&amp;Gaps=no_gaps&amp;store_dic=&amp;is_refire=true&amp;Fam_or_Word=multi&amp;Source=http%3A%2F%2Fwww.lextutor.ca%2Fconc%2Feng%2F&amp;unframed=true&amp;SearchType=family&amp;SearchStr=[[term]]&amp;Corpus=brown_strip.txt&amp;ColloSize=1&amp;SortType=left&amp;AssocWord=&amp;AssocSide=left
```

이는 lextutor라는 사이트에서 특정 단어를 검색하기 위한 명령인데요. 해당 웹페이지에서 검색하면 검색한 단어가 포함되어 영어권에서 작성된 논문이나 소설, 리포트 등의 문장이 결과에 표시됩니다. 이를 통해서 내가 검색해보고자 하는 단어가 실제 텍스트에서 어떠한 맥락으로 사용되는지에 대한 힌트를 얻을 수가 있습니다.

앞에서는 Action에 대해서만 설명을 드렸는데, 사전앱이니 만큼 인터넷에 연결되어 있지 않거나 별도의 Action을 실행하지 않아도 물론 단어의 뜻을 찾아볼 수 있습니다. 기본 사전은 Princeton 대학교의 Wordnet 프로젝트를 활용하고 있다고 합니다.

저는 Terminology 2를 처음 구입한 것을 시작으로 현재까지 매우 유용하게 사용하고 있습니다. 물론 가끔 Longman 등에서 나온 사전앱의 그림 설명이나 단어 게임 등이 부럽기도 하지만, 어차피 잘 안 본다는 것을 알고 있기도 하고, 비슷한 기능을 하는 앱을 여럿 두는 것도 좋아하지 않아서 이것 하나만 쓰고 있습니다. 정 필요하면 이 앱을 통해서 바로 웹에 접속해 볼 수도 있으니 크게 불편하지 않습니다. 가볍고 확장성 좋은 사전앱을 찾으시는 분들께 추천합니다.

* * *

과거에 Writeup이라는 앱을 사용할 때는 영업 단어를 선택하면 "Te: Lookup" 또는 "Te: Replace" 라는 팝업 메뉴가 나와서 룩업을 선택하면 그 단어 뜻만 찾아보고 돌아오고, 리플레이스를 선택하면 터미놀로지에서 찾은 새로운 단어로 교체도 가능했는데, 기능을 제거한 것인지 이를 지원하는 앱이 더 이상 없는 것인지 지금 Editorial이나 Byword로 시도해 보니 작동이 되지 않네요. 이것도 자주 쓰지는 않지만 유용한 기능 중의 하나였습니다.


