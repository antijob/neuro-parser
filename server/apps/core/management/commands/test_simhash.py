# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.management import call_command

from server.apps.core.logic.grabber.actions import process_news


from simhash import SimhashIndex, Simhash
from server.apps.core.models import Article
import re
from server.apps.core.logic.reposts import get_reposts, calc_ratio



class Command(BaseCommand):
    def handle(self, *args, **options):
        index = SimhashIndex([], k=12)

        art = Article.objects.filter(is_downloaded=True, is_duplicate=False) 
        for a in art:
            if not a.text:
                continue
            text = re.sub(r'http\S+', '', a.text)

            sh = Simhash(text)
            near = index.get_near_dups(sh)
            if len(near) > 0:
                print("New simhash dub:")
                print(a.url)

                for x in near:
                    ratio = calc_ratio(Article.objects.get(url=x).text, a.text)
                    print(x, ratio)

            index.add(a.url, sh)

        art = Article.objects.filter(is_downloaded=True, is_duplicate=True)
        for a in art:
            if not a.text:
                continue

            text = re.sub(r'http\S+', '', a.text)
            sh = Simhash(text)

            near = index.get_near_dups(sh)
            if len(near) == 0:
                print("Missed in simhash dub:")
                print(a.url)
                _, repost = get_reposts(a.text)
                if repost:
                    print(repost.url, self.compare(repost.url, a.url))

    def compare(self, url1, url2):
        sh1 = Simhash(Article.objects.get(url=url1).text)
        sh2 = Simhash(Article.objects.get(url=url2).text)
        return sh1.distance(sh2)
