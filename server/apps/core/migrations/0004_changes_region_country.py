from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_data_region_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediaincident',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.country'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='source',
            name='country',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.country'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mediaincident',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.region'),
        ),
        migrations.AlterField(
            model_name='source',
            name='region',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.region'),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(choices=[('ALL', 'Все регионы'), ('RU-AMU', 'Амурская область'), ('RU-ARK', 'Архангельская область'), ('RU-AST', 'Астраханская область'), ('RU-BEL', 'Белгородская область'), ('RU-BRY', 'Брянская область'), ('RU-VLA', 'Владимирская область'), ('RU-VGG', 'Волгоградская область'), ('RU-VLG', 'Вологодская область'), ('RU-VOR', 'Воронежская область'), ('RU-IVA', 'Ивановская область'), ('RU-IRK', 'Иркутская область'), ('RU-KGD', 'Калининградская область'), ('RU-KLU', 'Калужская область'), ('RU-KEM', 'Кемеровская область'), ('RU-KIR', 'Кировская область'), ('RU-KOS', 'Костромская область'), ('RU-KGN', 'Курганская область'), ('RU-KRS', 'Курская область'), ('RU-LEN', 'Ленинградская область'), ('RU-LIP', 'Липецкая область'), ('RU-MAG', 'Магаданская область'), ('RU-MOS', 'Московская область'), ('RU-MUR', 'Мурманская область'), ('RU-NIZ', 'Нижегородская область'), ('RU-NGR', 'Новгородская область'), ('RU-NVS', 'Новосибирская область'), ('RU-OMS', 'Омская область'), ('RU-ORE', 'Оренбургская область'), ('RU-ORL', 'Орловская область'), ('RU-PNZ', 'Пензенская область'), ('RU-PSK', 'Псковская область'), ('RU-ROS', 'Ростовская область'), ('RU-RYA', 'Рязанская область'), ('RU-SAM', 'Самарская область'), ('RU-SAR', 'Саратовская область'), ('RU-SAK', 'Сахалинская область'), ('RU-SVE', 'Свердловская область'), ('RU-SMO', 'Смоленская область'), ('RU-TAM', 'Тамбовская область'), ('RU-TVE', 'Тверская область'), ('RU-TOM', 'Томская область'), ('RU-TUL', 'Тульская область'), ('RU-TYU', 'Тюменская область'), ('RU-ULY', 'Ульяновская область'), ('RU-CHE', 'Челябинская область'), ('RU-YAR', 'Ярославская область'), ('RU-AD', 'Республика Адыгея'), ('RU-BA', 'Республика Башкортостан'), ('RU-BU', 'Республика Бурятия'), ('RU-DA', 'Республика Дагестан'), ('RU-IN', 'Республика Ингушетия'), ('RU-KB', 'Кабардино-Балкарская Республика'), ('RU-KL', 'Республика Калмыкия'), ('RU-KC', 'Карачаево-Черкесская Республика'), ('RU-KR', 'Республика Карелия'), ('UA-43', 'Республика Крым'), ('RU-ME', 'Республика Марий Эл'), ('RU-MO', 'Республика Мордовия'), ('RU-AL', 'Республика Алтай'), ('RU-KO', 'Республика Коми'), ('RU-SA', 'Республика Саха (Якутия)'), ('RU-SE', 'Республика Северная Осетия — Алания'), ('RU-TA', 'Республика Татарстан'), ('RU-TY', 'Республика Тыва'), ('RU-UD', 'Удмуртская Республика'), ('RU-KK', 'Республика Хакасия'), ('RU-CE', 'Чеченская Республика'), ('RU-CU', 'Чувашская Республика'), ('RU-ALT', 'Алтайский край'), ('RU-ZAB', 'Забайкальский край'), ('RU-KAM', 'Камчатский край'), ('RU-KDA', 'Краснодарский край'), ('RU-KYA', 'Красноярский край'), ('RU-PER', 'Пермский край'), ('RU-PRI', 'Приморский край'), ('RU-STA', 'Ставропольский край'), ('RU-KHA', 'Хабаровский край'), ('RU-NEN', 'Ненецкий автономный округ'), ('RU-KHM', 'Ханты-Мансийский автономный округ — Югра'), ('RU-CHU', 'Чукотский автономный округ'), ('RU-YAN', 'Ямало-Ненецкий автономный округ'), ('RU-YEV', 'Еврейская автономная область'), ('RU-SPE', 'Санкт-Петербург'), ('RU-MOW', 'Москва'), ('UA-40', 'Севастополь')], default='ALL', max_length=100, verbose_name='Регион'),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(choices=[('ALL', 'Все страны из списка'), ('ARM', 'Армения'), ('AZE', 'Азербайджан'), ('BLR', 'Беларусь'), ('EST', 'Эстония'), ('GEO', 'Грузия'), ('KAZ', 'Казахстан'), ('KGZ', 'Киргизия'), ('LVA', 'Латвия'), ('LTU', 'Литва'), ('MDA', 'Молдова'), ('RUS', 'Россия'), ('TJK', 'Таджикистан'), ('TKM', 'Туркменистан'), ('UKR', 'Украина'), ('UZB', 'Узбекистан'), ('DEU', 'Германия')], default='ALL', max_length=100, verbose_name='Страна'),
        ),
        migrations.AlterField(
            model_name='source',
            name='country',
            field=models.ForeignKey(blank=True, default=33, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.country'),
        ),
        migrations.AlterField(
            model_name='source',
            name='region',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.region'),
        ),
        migrations.AlterField(
            model_name='source',
            name='country',
            field=models.ForeignKey(blank=True, default=11, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.country'),
        ),
        migrations.AlterField(
            model_name='source',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.country'),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(choices=[('ALL', 'Все страны из списка'), ('ARM', 'Армения'), ('AZE', 'Азербайджан'), ('BLR', 'Беларусь'), ('EST', 'Эстония'), ('GEO', 'Грузия'), ('KAZ', 'Казахстан'), ('KGZ', 'Киргизия'), ('LVA', 'Латвия'), ('LTU', 'Литва'), ('MDA', 'Молдова'), ('RUS', 'Россия'), ('TJK', 'Таджикистан'), ('TKM', 'Туркменистан'), ('UKR', 'Украина'), ('UZB', 'Узбекистан'), ('DEU', 'Германия')], default='RUS', max_length=100, verbose_name='Страна'),
        ),
        migrations.AlterField(
            model_name='source',
            name='country',
            field=models.ForeignKey(default=11, on_delete=django.db.models.deletion.CASCADE, to='core.country'),
        ),
    ]
