# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.management import call_command

from simhash import SimhashIndex, Simhash
from server.apps.core.models import Article
import re
from server.apps.simhash.reposts import get_orig, calc_ratio
import logging


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig()
        sh_log = logging.getLogger().setLevel(logging.ERROR)
        index = SimhashIndex([], k=10, log=sh_log)

        art = Article.objects.filter(is_downloaded=True, is_duplicate=False)
        for a in art:
            if not a.text:
                continue
            text = re.sub(r"http\S+", "", a.text)

            sh = Simhash(text)
            near = index.get_near_dups(sh)
            if len(near) > 0:
                print("New simhash dub:")
                print(a.url)

                for x in near:
                    near_text = Article.objects.get(url=x).text
                    # near_text_no_links = re.sub(r'http\S+', '', near_text)
                    ratio = calc_ratio(near_text, a.text)
                    # nourl_ratio = calc_ratio(near_text_no_links, text)
                    print(x, ratio, self.compare(a.url, x))

            index.add(a.url, sh)

        art = Article.objects.filter(is_downloaded=True, is_duplicate=True)
        for a in art:
            if not a.text:
                continue

            text = re.sub(r"http\S+", "", a.text)
            sh = Simhash(text)

            near = index.get_near_dups(sh)
            if len(near) == 0:
                _, repost = get_orig(a.text)
                if repost:
                    print("Missed in simhash dub:")
                    print(a.url)
                    print(repost.url, self.compare(repost.url, a.url))

    def compare(self, url1, url2):
        text1 = Article.objects.get(url=url1).text
        text2 = Article.objects.get(url=url2).text
        text1 = re.sub(r"http\S+", "", text1)
        text2 = re.sub(r"http\S+", "", text2)
        sh1 = Simhash(text1)
        sh2 = Simhash(text2)
        return sh1.distance(sh2)
