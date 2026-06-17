from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer, OfferCategory

PAUSED_NOTICE = (
    "\n\n⚠️ <i>В данный момент набор в твоем городе приостановлен, все места заняты. "
    "Рекомендуем обратить внимание на категорию «Доставка» или «Удаленка» — там сейчас "
    "открыты горячие слоты с повышенной оплатой.</i>"
)


def build_offers() -> list[Offer]:
    return [
        # ── Доставка и логистика ─────────────────────────────────────────
        Offer(
            title="Яндекс.Еда — Курьер (пеший / вело / авто)",
            category=OfferCategory.DELIVERY,
            short_description=(
                "Официальный партнер сервиса Яндекс.Еда приглашает к сотрудничеству курьеров "
                "для доставки заказов из ресторанов и магазинов. Ты можешь выполнять доставки "
                "пешком, на велосипеде, самокате или личном автомобиле в удобном районе."
            ),
            benefits=(
                "• Выплаты для велокурьеров до 3400 ₽ в день\n"
                "• Повышенный приоритет на заказах для вело- и автокурьеров\n"
                "• Гибкое расписание, которое ты выбираешь сам (смены от 2 часов)\n"
                "• Удобные локации в городе рядом с домом или учебой\n"
                "• Официальные партнеры сервиса, у которых можно арендовать транспорт\n"
                "• Бесплатная экипировка выдается в курьерском центре\n"
                "• Требования: телефон на базе Android 7+ или iPhone с iOS 13+"
            ),
            salary_info="до 3400 ₽ в день на вело / выше на авто",
            referral_link=(
                "https://advt.pro/product/ProductId~01HM6F39WYNVS7SKCPFF7KBANC!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="🚀 Занять рабочее место",
            image_path="assets/yandex_delivery.jpg",
            payout=8000.0,
            sort_order=1,
        ),
        Offer(
            title="Самокат — Курьер доставки",
            category=OfferCategory.DELIVERY,
            short_description=(
                "Доставка собранных интернет-заказов (продукты питания и товары для дома) "
                "из дарксторов до клиентов. Работа ведется в пределах одного района."
            ),
            benefits=(
                "• Гарантированный доход за каждый час смены\n"
                "• Полное отсутствие штрафов и скрытых удержаний\n"
                "• Бесплатный корпоративный электровелосипед\n"
                "• Еженедельные стабильные выплаты на карту\n"
                "• Выбор даркстора в удобном районе города"
            ),
            salary_info="стабильная оплата за час смены",
            referral_link=(
                "https://advt.pro/product/ProductId~01HM6EGR30ZE687GB4FX2BN65B!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="🚀 Занять рабочее место",
            image_path="assets/samokat_delivery.jpg",
            payout=6500.0,
            sort_order=2,
        ),
        Offer(
            title="Купер — Сборщик заказов",
            category=OfferCategory.DELIVERY,
            short_description=(
                "Работа в торговых сетях и гипермаркетах: комплектация продуктов и товаров "
                "по мобильному приложению, контроль сроков годности."
            ),
            benefits=(
                "• Стабильный доход со своевременными выплатами\n"
                "• Комфортные условия труда внутри торгового зала\n"
                "• Гибкие графики и смены на выбор\n"
                "• Быстрое обучение на месте со дня оформления\n"
                "• Корпоративные бонусы и помощь с медкнижкой"
            ),
            salary_info="от 55 000 ₽/мес при полной занятости",
            referral_link=(
                "https://advt.pro/product/ProductId~01J2GSVBR5RXA5RH0ECRCSZ57G!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/kuper_picker.jpg",
            payout=7000.0,
            sort_order=3,
        ),
        Offer(
            title="Купер — Пеший курьер",
            category=OfferCategory.DELIVERY,
            short_description=(
                "Доставка укомплектованных заказов из гипермаркетов до дверей клиентов "
                "в ближайшем радиусе от торговой точки."
            ),
            benefits=(
                "• Смены от 4 часов на выбор\n"
                "• Высокий доход + 100% чаевых остаются тебе\n"
                "• Доплаты за крупногабаритные заказы\n"
                "• Минимальный радиус доставки\n"
                "• Компенсация за оформление медкнижки"
            ),
            salary_info="до 3500 ₽ за смену в пиковые дни",
            referral_link=(
                "https://advt.pro/product/ProductId~01J2GSK81XB4WS6YC2P5DZFYDP!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/kuper_courier.jpg",
            payout=6000.0,
            sort_order=4,
        ),
        # ── Трудоустройство и вакансии ───────────────────────────────────
        Offer(
            title="Карьера в Т-Банке (более 20 вакансий)",
            category=OfferCategory.JOBS,
            short_description=(
                "Крупнейший онлайн-банк приглашает специалистов на дистанционные, офисные "
                "и разъездные направления: поддержка, продажи, премиум, антифрод, маркетинг."
            ),
            benefits=(
                "• Вакансии из офиса, удаленные и разъездные\n"
                "• Стабильная компания с официальным оформлением\n"
                "• Карьерный рост и гибкий график\n"
                "• Обучение и наставник с первого дня\n"
                "• Развитие внутри компании\n"
                "• Сильная команда коллег"
            ),
            salary_info="по выбранной вакансии, без задержек",
            referral_link=(
                "https://advt.pro/product/ProductId~01JNNEMEZ5VVW1BC1ZWVNNGVW5!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/tbank_career.jpg",
            payout=10000.0,
            sort_order=1,
        ),
        Offer(
            title="Альфа-Банк — Специалист по доставке карт",
            category=OfferCategory.JOBS,
            short_description=(
                "Официальное представительство банка в твоем городе: доставка карт и документов, "
                "проверка данных и консультирование клиентов."
            ),
            benefits=(
                "• Фиксированный оклад + премии за доставку\n"
                "• Гибкий график — планируешь дни сам\n"
                "• Компенсация транспорта\n"
                "• Корпоративная связь и смартфон\n"
                "• Переход на управленческие позиции"
            ),
            salary_info="оклад + премии за каждую доставку",
            referral_link=(
                "https://advt.pro/product/ProductId~01J3N23ZDX1BXKBS1279RRT1P0!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/alfa_delivery_job.jpg",
            payout=12000.0,
            sort_order=2,
        ),
        Offer(
            title="МТС — Оператор call-центра (удаленно)",
            category=OfferCategory.REMOTE,
            short_description=(
                "Дистанционная работа в экосистеме цифровых сервисов: консультации клиентов "
                "по тарифам, услугам связи и домашнему интернету."
            ),
            benefits=(
                "• 100% удаленно из любой точки РФ\n"
                "• Официальное оформление по ТК РФ\n"
                "• Оклад + ежемесячные премии\n"
                "• Скидки на связь и интернет МТС\n"
                "• Сменные графики, можно совмещать"
            ),
            salary_info="от 35 000 ₽/мес + премии",
            referral_link=(
                "https://advt.pro/product/ProductId~01HY36PSJFRT93W047CR7ZH2KR!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/mts_support.jpg",
            payout=5000.0,
            sort_order=1,
        ),
        Offer(
            title="МТС — Специалист по продажам услуг",
            category=OfferCategory.JOBS,
            short_description=(
                "Привлечение новых клиентов и продвижение цифровых продуктов связи "
                "(интернет, ТВ, мобильная связь) по готовой базе."
            ),
            benefits=(
                "• Неограниченный заработок — процент с каждой сделки\n"
                "• Гибкий график — удобно студентам\n"
                "• Тренинги по продажам за счет компании\n"
                "• Официальное оформление\n"
                "• Старт карьеры в крупной IT/телеком компании"
            ),
            salary_info="оклад + % от сделок",
            referral_link=(
                "https://advt.pro/product/ProductId~01HY371EQSXHNT4GHSY5S3W6XG!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/mts_sales.jpg",
            payout=6000.0,
            sort_order=3,
        ),
        # ── Банковские карты ─────────────────────────────────────────────
        Offer(
            title="Т-Банк — Кредитная карта Platinum | Кэшбэк 2000 ₽",
            category=OfferCategory.BANKING,
            short_description=(
                "Флагманская кредитная карта Т-Банка с одобрением онлайн. Покупки в рассрочку "
                "и без процентов в льготный период."
            ),
            benefits=(
                "• Кэшбэк 2000 ₽ реальными деньгами после условий по тратам\n"
                "• Бесплатное обслуживание навсегда\n"
                "• Беспроцентный период до 55 дней на покупки\n"
                "• До 120 дней на погашение других кредитов\n"
                "• Рассрочка до 12 месяцев без %\n"
                "• Бесплатные переводы на любые карты\n"
                "• Доставка карты на дом"
            ),
            salary_info="кэшбэк 2000 ₽ + льготный период",
            referral_link=(
                "https://advt.pro/product/ProductId~01KQS3F211JKJG7H8RJM97XS28!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/tbank_platinum.jpg",
            payout=10000.0,
            sort_order=1,
        ),
        Offer(
            title="Газпромбанк — Дебетовая «Умная карта»",
            category=OfferCategory.BANKING,
            short_description=(
                "Дебетовая карта, которая подстраивается под твои расходы и максимизирует выгоду."
            ),
            benefits=(
                "• Акция «Двойной кэшбэк» первые 2 месяца\n"
                "• Умный кэшбэк на категорию максимальных трат\n"
                "• Бесплатное обслуживание\n"
                "• Снятие наличных и переводы по СБП"
            ),
            salary_info="повышенный кэшбэк в выбранных категориях",
            referral_link=(
                "https://advt.pro/product/ProductId~01GT78K1X9G9AMGXXZYPG640E8!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/gpb_smart.jpg",
            payout=8500.0,
            sort_order=2,
        ),
        Offer(
            title="Альфа-Банк — Молодежная дебетовая карта",
            category=OfferCategory.BANKING,
            short_description=(
                "Карта для молодых клиентов: финансы, развлечения и повышенные бонусы."
            ),
            benefits=(
                "• 0 ₽ за обслуживание навсегда\n"
                "• До 5000 ₽ каждый месяц с суперкэшбэком\n"
                "• До 30% кэшбэка в категориях на выбор\n"
                "• Бесплатные переводы до 100 000 ₽ по СБП\n"
                "• Оплата игр, музыки и сервисов"
            ),
            salary_info="до 30% кэшбэк в выбранных категориях",
            referral_link=(
                "https://advt.pro/product/ProductId~01K5EEW9PEDNGGDDCM9G7K26KF!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/alfa_youth.jpg",
            payout=12000.0,
            sort_order=3,
        ),
        Offer(
            title="Газпромбанк — Кредитная карта «115 дней без %»",
            category=OfferCategory.BANKING,
            short_description=(
                "Кредитная карта с длинным льготным периодом для крупных покупок без переплат."
            ),
            benefits=(
                "• Беспроцентный период до 115 дней\n"
                "• Бесплатное обслуживание первый год\n"
                "• Быстрое онлайн-одобрение\n"
                "• Снятие наличных в рамках лимитов\n"
                "• Льготный период на покупки онлайн и офлайн"
            ),
            salary_info="до 115 дней без процентов",
            referral_link=(
                "https://advt.pro/product/ProductId~01KRGYPQP8XFJ27KQMG2ZC7D6Q!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/gpb_115.jpg",
            payout=11000.0,
            sort_order=4,
        ),
        Offer(
            title="ВТБ — Дебетовая карта",
            category=OfferCategory.BANKING,
            short_description=(
                "Надежный расчетный инструмент от крупного банка: хранение, переводы, гарантии."
            ),
            benefits=(
                "• Приветственный кэшбэк до 25% в первые месяцы\n"
                "• Бесплатное обслуживание навсегда\n"
                "• Бесплатные переводы по СБП\n"
                "• Привилегии по накопительным счетам ВТБ"
            ),
            salary_info="кэшбэк до 25% на старте",
            referral_link=(
                "https://advt.pro/product/ProductId~01H7ZDRJRFP11BT5FQFN7G6H00!"
                "ExecutorId~01KQP35S45P0J8X3EBYCME23YY!UserId~01KQP35RE57NB9J5C8PW83KAG6?w_method=app"
            ),
            cta_text="📝 Заполнить анкету",
            image_path="assets/vtb_debit.jpg",
            payout=8500.0,
            sort_order=5,
        ),
        # ── Подработка (приостановленный набор) ──────────────────────────
        Offer(
            title="Тайный покупатель",
            category=OfferCategory.BEGINNER,
            short_description="Проверка сервиса в магазинах, кафе и банках по чек-листу." + PAUSED_NOTICE,
            benefits=(
                "• Гибкий график заданий\n"
                "• Компенсация покупки + гонорар\n"
                "• Оплата за каждый отчет"
            ),
            salary_info="от 500 ₽ за визит",
            referral_link="https://t.me/Workora_student",
            cta_text="📝 Заполнить анкету",
            image_path="assets/beginner_mystery.jpg",
            is_paused=True,
            sort_order=1,
        ),
        Offer(
            title="Промоутер на мероприятиях",
            category=OfferCategory.BEGINNER,
            short_description="Раздача материалов, работа на стойке, приглашение гостей." + PAUSED_NOTICE,
            benefits=(
                "• Старт без опыта\n"
                "• Оплата в день смены\n"
                "• Можно совмещать с учебой"
            ),
            salary_info="от 1800 ₽ за смену",
            referral_link="https://t.me/Workora_student",
            cta_text="📝 Заполнить анкету",
            image_path="assets/beginner_promo.jpg",
            is_paused=True,
            sort_order=2,
        ),
    ]


async def seed_database(session: AsyncSession) -> int:
    """Upsert offers by title — safe to call on every bot startup."""
    count = 0
    for offer_data in build_offers():
        result = await session.execute(
            select(Offer).where(Offer.title == offer_data.title),
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.category = offer_data.category
            existing.short_description = offer_data.short_description
            existing.benefits = offer_data.benefits
            existing.salary_info = offer_data.salary_info
            existing.bonuses = offer_data.bonuses
            existing.image_path = offer_data.image_path
            existing.referral_link = offer_data.referral_link
            existing.payout = offer_data.payout
            existing.cta_text = offer_data.cta_text
            existing.is_active = offer_data.is_active
            existing.is_paused = offer_data.is_paused
            existing.sort_order = offer_data.sort_order
        else:
            session.add(offer_data)
        count += 1
    await session.flush()
    return count
