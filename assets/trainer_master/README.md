# Master Trainer assets / «Утро 7»

**Текущий статус: T0 — подготовка технологии. Модель человека пока не создана.**

- **master_manifest.json** — машиночитаемые статусы, идентификатор будущего тренера и обязательные ракурсы.
- **scenes/utro7_studio_template.blend** — нейтральная студийная сцена Blender (7 камер, 3 источника света, плоскость пола). **Не содержит человеческой модели.**
- **renders/** — будущие семь контрольных ракурсов одного и того же реального 3D-персонажа.
- **poses/** — будущие восемь диагностических поз (после визуальной приёмки).

Собрать сцену повторно на Mac:

    blender -b -t 6 -P tools/blender/trainer_master/create_studio.py

Проверить её:

    blender -b -t 4 assets/trainer_master/scenes/utro7_studio_template.blend -P tools/blender/trainer_master/validate_studio.py

**Важно:** исходные коммерческие 3D-модели, их текстуры, волосы и одежду нельзя добавлять в публичный репозиторий без подтверждения лицензии на перераспространение. Приватные source и installer следует хранить вне Git; в репозиторий публикуем только разрешённые производные рендеры и код. Рабочая лицензия, vendor и версия должны быть описаны в provenance до первого пользовательского ревью.

[Мастер-ТЗ](../../docs/UTRO7_MASTER_TRAINER_TZ.md) · [Чек-лист](../../docs/TRAINER_MASTER_ACCEPTANCE_CHECKLIST.md) · [Issue #6](https://github.com/Dmitriy-Bondarev/utro7/issues/6).
