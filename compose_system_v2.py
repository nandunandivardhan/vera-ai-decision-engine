
import json
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, Tuple


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1: ENUMS & DATA MODELS
# ═════════════════════════════════════════════════════════════════════════════

class Category(Enum):
    RESTAURANT = "restaurant"
    SALON = "salon"
    GROCERY = "grocery"
    FASHION = "fashion"


class CustomerType(Enum):
    NEW = "new"
    REGULAR = "regular"
    INACTIVE = "inactive"


class TimeContext(Enum):
    LUNCH = "lunch"
    DINNER = "dinner"
    BREAKFAST = "breakfast"
    OFF_PEAK = "off_peak"


class DemandLevel(Enum):
    CRITICAL = "critical"
    HIGH_DROP = "high_drop"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class ActionType(Enum):
    DISCOUNT = "discount"
    LOYALTY = "loyalty"
    URGENCY = "urgency"
    UPSELL = "upsell"
    REMINDER = "reminder"
    WELCOME = "welcome"
    REACTIVATION = "reactivation"


class Strategy(Enum):
    ACQUISITION = "acquisition"
    RETENTION = "retention"
    REACTIVATION = "reactivation"
    MONETIZATION = "monetization"
    URGENCY = "urgency"


@dataclass
class BusinessSignals:
    category: Category
    merchant: str
    trigger: str
    customer_type: CustomerType
    demand_level: DemandLevel
    time_context: TimeContext
    days_since_last_purchase: Optional[int] = None
    customer_value_tier: str = "standard"
    external_factor: Optional[str] = None


@dataclass
class Decision:
    action: ActionType
    strategy: Strategy
    offer_percentage: int
    confidence_score: float
    reasoning: str
    priority: int
    cta_text: str
    personalization_level: str


@dataclass
class Message:
    content: str
    decision: Decision
    quality_score: float
    category_tone: str
    urgency_level: str
    estimated_conversion_impact: str


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2: IMPROVED CONTEXT ANALYZER
# ═════════════════════════════════════════════════════════════════════════════

class ContextAnalyzer:
    """Enhanced context analyzer with trigger-aware time classification."""

    @staticmethod
    def classify_demand(trigger: str, category: Category) -> DemandLevel:
        trigger_lower = trigger.lower()

        critical_signals = ["critical_drop", "zero_sales", "emergency", "shutdown"]
        if any(sig in trigger_lower for sig in critical_signals):
            return DemandLevel.CRITICAL

        drop_signals = ["steep_drop", "plummeting", "massive_drop", "nosedive"]
        if any(sig in trigger_lower for sig in drop_signals):
            return DemandLevel.HIGH_DROP

        low_signals = ["slow", "quiet", "low_traffic", "sparse", "weak"]
        if any(sig in trigger_lower for sig in low_signals):
            return DemandLevel.LOW

        high_signals = ["peak", "rush", "packed", "full", "surge", "trending"]
        if any(sig in trigger_lower for sig in high_signals):
            return DemandLevel.HIGH

        return DemandLevel.NORMAL

    @staticmethod
    def classify_time_context(
        hour: Optional[int] = None, trigger: Optional[str] = None
    ) -> TimeContext:
        """
        FIXED: Now accepts trigger parameter for intelligent inference.
        Trigger can override actual time.
        """
        # Trigger-based overrides (more intelligent)
        if trigger:
            trigger_lower = trigger.lower()
            if "lunch" in trigger_lower:
                return TimeContext.LUNCH
            elif "dinner" in trigger_lower or "rush" in trigger_lower:
                return TimeContext.DINNER
            elif "peak_lunch" in trigger_lower:
                return TimeContext.LUNCH
            elif "peak_booking" in trigger_lower:
                return TimeContext.DINNER

        # Default time-based classification
        if hour is None:
            hour = datetime.now().hour

        if 7 <= hour < 10:
            return TimeContext.BREAKFAST
        elif 11 <= hour < 14:
            return TimeContext.LUNCH
        elif 18 <= hour < 21:
            return TimeContext.DINNER
        else:
            return TimeContext.OFF_PEAK

    @staticmethod
    def classify_customer_type(days_since_purchase: Optional[int]) -> CustomerType:
        if days_since_purchase is None or days_since_purchase == -1:
            return CustomerType.NEW
        if days_since_purchase <= 90:
            return CustomerType.REGULAR
        return CustomerType.INACTIVE

    @staticmethod
    def extract_signals(
        category: Category,
        merchant: str,
        trigger: str,
        customer: Optional[Dict] = None,
    ) -> BusinessSignals:
        days_since_purchase = None
        customer_type = CustomerType.NEW
        customer_value_tier = "standard"

        if customer:
            days_since_purchase = customer.get("days_since_last_purchase")
            customer_type = ContextAnalyzer.classify_customer_type(
                days_since_purchase
            )
            customer_value_tier = customer.get("value_tier", "standard")

        demand_level = ContextAnalyzer.classify_demand(trigger, category)
        time_context = ContextAnalyzer.classify_time_context(None, trigger)  # FIX: Pass trigger
        external_factor = ContextAnalyzer.extract_external_factor(trigger)

        return BusinessSignals(
            category=category,
            merchant=merchant,
            trigger=trigger,
            customer_type=customer_type,
            demand_level=demand_level,
            time_context=time_context,
            days_since_last_purchase=days_since_purchase,
            customer_value_tier=customer_value_tier,
            external_factor=external_factor,
        )

    @staticmethod
    def extract_external_factor(trigger: str) -> Optional[str]:
        trigger_lower = trigger.lower()
        factors = ["festival", "holiday", "weekend", "promotion", "sale", "launch"]
        for factor in factors:
            if factor in trigger_lower:
                return factor
        return None


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3: ENHANCED DECISION ENGINE
# ═════════════════════════════════════════════════════════════════════════════

class DecisionEngine:
    """
    IMPROVED: Enhanced strategy selection with peak-hour awareness.
    """

    @staticmethod
    def select_strategy(signals: BusinessSignals) -> Tuple[Strategy, str]:
        """
        Enhanced strategy selection with new rule for peak hours.
        """

        # Rule 1: New customers = Acquisition
        if signals.customer_type == CustomerType.NEW:
            return (
                Strategy.ACQUISITION,
                "Welcome first-time customer with onboarding offer",
            )

        # Rule 2: Inactive customers = Reactivation
        if signals.customer_type == CustomerType.INACTIVE:
            return (
                Strategy.REACTIVATION,
                "Win back dormant customer with special incentive",
            )

        # ENHANCED Rule 3: Peak hours + high demand + regular = URGENCY (not monetization)
        if (
            signals.demand_level == DemandLevel.HIGH
            and signals.time_context in [TimeContext.LUNCH, TimeContext.DINNER]
            and signals.customer_type == CustomerType.REGULAR
        ):
            return (
                Strategy.URGENCY,
                "Capitalize on peak-hour momentum with existing customer",
            )

        # Rule 4: Severe demand drop + regular = Retention
        if signals.demand_level in [DemandLevel.CRITICAL, DemandLevel.HIGH_DROP]:
            if signals.customer_type == CustomerType.REGULAR:
                return (
                    Strategy.RETENTION,
                    "Protect regular customer during low-demand period",
                )

        # Rule 5: Normal/healthy demand + regular + premium tier = Monetization
        if (
            signals.demand_level == DemandLevel.NORMAL
            and signals.customer_type == CustomerType.REGULAR
            and signals.customer_value_tier == "vip"
        ):
            return (Strategy.MONETIZATION, "Upsell premium tier customer")

        # ENHANCED Rule 6: High demand + new customer = aggressive acquisition
        if (
            signals.demand_level == DemandLevel.HIGH
            and signals.customer_type == CustomerType.NEW
        ):
            return (
                Strategy.ACQUISITION,
                "Capture new customer during high-traffic opportunity",
            )

        # Rule 7: Low demand + regular = Retention with incentive
        if (
            signals.demand_level == DemandLevel.LOW
            and signals.customer_type == CustomerType.REGULAR
        ):
            return (
                Strategy.RETENTION,
                "Stimulate demand from existing customer base",
            )

        # Default: Monetization
        return (Strategy.MONETIZATION, "Optimize customer lifetime value")

    @staticmethod
    def select_action(strategy: Strategy, signals: BusinessSignals) -> ActionType:
        strategy_to_action = {
            Strategy.ACQUISITION: ActionType.WELCOME,
            Strategy.REACTIVATION: ActionType.REACTIVATION,
            Strategy.RETENTION: ActionType.LOYALTY,
            Strategy.MONETIZATION: ActionType.UPSELL,
            Strategy.URGENCY: ActionType.URGENCY,
        }
        return strategy_to_action.get(strategy, ActionType.REMINDER)

    @staticmethod
    def calculate_offer_percentage(
        action: ActionType,
        demand_level: DemandLevel,
        customer_type: CustomerType,
        category: Category,
    ) -> int:
        """
        Enhanced offer calculation with better demand weighting.
        """

        base_offers = {
            ActionType.WELCOME: 18,
            ActionType.DISCOUNT: 20,
            ActionType.LOYALTY: 12,
            ActionType.UPSELL: 8,
            ActionType.URGENCY: 22,  # INCREASED from 20
            ActionType.REACTIVATION: 26,  # INCREASED from 25
            ActionType.REMINDER: 3,
        }

        offer = base_offers.get(action, 10)

        # Enhanced demand boost
        demand_boost = {
            DemandLevel.CRITICAL: 12,  # INCREASED from 10
            DemandLevel.HIGH_DROP: 7,  # INCREASED from 5
            DemandLevel.LOW: 5,  # INCREASED from 3
            DemandLevel.NORMAL: 0,
            DemandLevel.HIGH: 0,
        }
        offer += demand_boost.get(demand_level, 0)

        # Customer type modifier
        if customer_type == CustomerType.REGULAR:
            offer -= 3  # REDUCED from 5 (less aggressive discount)

        # Category impact
        category_boost = {
            Category.RESTAURANT: 5,
            Category.SALON: 3,
            Category.GROCERY: -1,  # IMPROVED from -2
            Category.FASHION: 2,
        }
        offer += category_boost.get(category, 0)

        return max(10, min(40, offer))

    @staticmethod
    def calculate_confidence(
        strategy: Strategy, signals: BusinessSignals, action: ActionType
    ) -> float:
        """
        IMPROVED: Expanded confidence range with more nuance.
        """
        confidence = 0.60  # Lower baseline for better range

        # Strong signal matches (major boosts)
        if signals.demand_level == DemandLevel.CRITICAL:
            confidence += 0.20

        if (
            signals.demand_level == DemandLevel.HIGH_DROP
            and signals.customer_type == CustomerType.REGULAR
        ):
            confidence += 0.18

        # Customer-strategy matching
        if signals.customer_type == CustomerType.NEW:
            if strategy == Strategy.ACQUISITION:
                confidence += 0.18

        if signals.customer_type == CustomerType.INACTIVE:
            if strategy == Strategy.REACTIVATION:
                confidence += 0.18

        # Peak hour matching
        if signals.time_context in [TimeContext.LUNCH, TimeContext.DINNER]:
            if signals.demand_level == DemandLevel.HIGH:
                confidence += 0.12

        # External factor boost
        if signals.external_factor:
            confidence += 0.08

        # Action-specific boosts
        if action == ActionType.URGENCY and signals.time_context in [
            TimeContext.LUNCH,
            TimeContext.DINNER,
        ]:
            confidence += 0.05

        return min(0.98, confidence)

    @staticmethod
    def calculate_priority(
        strategy: Strategy,
        demand_level: DemandLevel,
        customer_type: CustomerType,
    ) -> int:
        """
        SAME LOGIC (working well)
        """

        if demand_level == DemandLevel.CRITICAL:
            return 10

        if demand_level == DemandLevel.HIGH_DROP and customer_type == CustomerType.REGULAR:
            return 9

        if customer_type == CustomerType.INACTIVE:
            return 8

        if customer_type == CustomerType.NEW:
            return 7

        if demand_level == DemandLevel.HIGH:
            return 6

        if customer_type == CustomerType.REGULAR:
            return 5

        return 3

    @staticmethod
    def generate_cta(
        action: ActionType,
        offer_percentage: int,
        category: Category,
        time_context: TimeContext,
        urgency_level: str,
    ) -> str:
        """
        IMPROVED: More dynamic urgency prefixes.
        """

        # Enhanced urgency modifiers
        if urgency_level == "high":
            if time_context in [TimeContext.LUNCH, TimeContext.DINNER]:
                urgency_prefix = "⏰ LIMITED TIME: "
            else:
                urgency_prefix = "🔥 Don't miss: "
        elif urgency_level == "medium":
            urgency_prefix = "⭐ "
        else:
            urgency_prefix = ""

        cta_map = {
            ActionType.WELCOME: f"{urgency_prefix}Claim welcome offer",
            ActionType.DISCOUNT: f"{urgency_prefix}Get {offer_percentage}% off",
            ActionType.LOYALTY: f"{urgency_prefix}Use loyalty reward",
            ActionType.UPSELL: f"{urgency_prefix}Unlock premium experience",
            ActionType.URGENCY: f"{urgency_prefix}Order now—{offer_percentage}% off",
            ActionType.REACTIVATION: f"{urgency_prefix}Come back today",
            ActionType.REMINDER: f"{urgency_prefix}Browse now",
        }

        return cta_map.get(action, "Explore more")

    @staticmethod
    def make_decision(signals: BusinessSignals) -> Decision:
        """Complete decision pipeline."""

        strategy, strategy_reason = DecisionEngine.select_strategy(signals)
        action = DecisionEngine.select_action(strategy, signals)
        offer_percentage = DecisionEngine.calculate_offer_percentage(
            action, signals.demand_level, signals.customer_type, signals.category
        )
        confidence = DecisionEngine.calculate_confidence(strategy, signals, action)
        priority = DecisionEngine.calculate_priority(
            strategy, signals.demand_level, signals.customer_type
        )

        urgency_level = "high" if priority >= 8 else "medium" if priority >= 5 else "low"
        cta_text = DecisionEngine.generate_cta(
            action, offer_percentage, signals.category, signals.time_context, urgency_level
        )

        personalization = (
            "deep" if signals.customer_type == CustomerType.REGULAR
            else "light"
        )

        reasoning = (
            f"Strategy: {strategy_reason}. "
            f"Customer: {signals.customer_type.value}. "
            f"Demand: {signals.demand_level.value}. "
            f"Time: {signals.time_context.value}. "
            f"Confidence: {confidence:.0%}."
        )

        return Decision(
            action=action,
            strategy=strategy,
            offer_percentage=offer_percentage,
            confidence_score=confidence,
            reasoning=reasoning,
            priority=priority,
            cta_text=cta_text,
            personalization_level=personalization,
        )


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4: ENHANCED SCORING ENGINE (FIXED)
# ═════════════════════════════════════════════════════════════════════════════

class ScoringEngine:
    """
    COMPLETELY REWRITTEN: All sub-scores now 0-100 scale independently.
    This fixes the normalization issue from v1.0.
    """

    @staticmethod
    def score_decision_quality(decision: Decision, signals: BusinessSignals) -> int:
        """
        Decision Quality (0-100).
        Measures: Is the decision intelligent and aligned?
        """
        score = 20  # baseline

        # Confidence scoring (40 points max)
        if decision.confidence_score >= 0.90:
            score += 40
        elif decision.confidence_score >= 0.80:
            score += 35
        elif decision.confidence_score >= 0.70:
            score += 30
        elif decision.confidence_score >= 0.60:
            score += 25
        else:
            score += 15

        # Priority scoring (35 points max)
        if decision.priority >= 9:
            score += 35
        elif decision.priority >= 7:
            score += 30
        elif decision.priority >= 5:
            score += 20
        else:
            score += 10

        # Offer appropriateness (25 points max)
        if 20 <= decision.offer_percentage <= 35:
            score += 25
        elif 15 <= decision.offer_percentage <= 40:
            score += 20
        else:
            score += 10

        return min(score, 100)

    @staticmethod
    def score_personalization(
        decision: Decision, signals: BusinessSignals
    ) -> int:
        """
        Personalization (0-100).
        Measures: How relevant is this to this customer?
        """
        score = 25  # baseline

        # Perfect customer-strategy match (50 points max)
        perfect_matches = [
            (Strategy.ACQUISITION, CustomerType.NEW),
            (Strategy.REACTIVATION, CustomerType.INACTIVE),
            (Strategy.RETENTION, CustomerType.REGULAR),
            (Strategy.URGENCY, CustomerType.REGULAR),
        ]

        is_matched = any(
            decision.strategy == s and signals.customer_type == c
            for s, c in perfect_matches
        )

        score += 50 if is_matched else 30

        # Category intelligence (30 points max)
        category_aware_actions = [
            ActionType.WELCOME,
            ActionType.LOYALTY,
            ActionType.REACTIVATION,
            ActionType.URGENCY,
        ]
        score += 30 if decision.action in category_aware_actions else 15

        # Customer value tier matching (20 points max)
        if signals.customer_value_tier == "vip" and decision.action in [
            ActionType.UPSELL,
            ActionType.LOYALTY,
        ]:
            score += 20
        elif signals.customer_value_tier == "atrisk" and decision.action in [
            ActionType.REACTIVATION,
            ActionType.LOYALTY,
        ]:
            score += 18
        else:
            score += 10

        return min(score, 100)

    @staticmethod
    def score_clarity(decision: Decision, message: Message) -> int:
        """
        Clarity (0-100).
        Measures: Is the message clear and actionable?
        """
        score = 20  # baseline

        # CTA quality (40 points max)
        good_ctas = [
            "claim",
            "order",
            "book",
            "get",
            "redeem",
            "unlock",
            "shop",
            "browse",
            "come back",
        ]
        if any(cta in decision.cta_text.lower() for cta in good_ctas):
            score += 40
        else:
            score += 25

        # Message structure (30 points max)
        if len(message.content) > 150:
            score += 15  # Too long
        elif len(message.content) > 80:
            score += 30  # Good length
        else:
            score += 25  # Concise

        # No vague language (30 points max)
        vague_words = ["maybe", "possibly", "might", "could be", "unclear"]
        if not any(vague in message.content.lower() for vague in vague_words):
            score += 30
        else:
            score += 10

        return min(score, 100)

    @staticmethod
    def score_business_impact(decision: Decision, signals: BusinessSignals) -> int:
        """
        Business Impact (0-100).
        Measures: Will this drive revenue?
        """
        score = 25  # baseline

        # Offer severity match (40 points max)
        if signals.demand_level == DemandLevel.CRITICAL:
            score += 40 if decision.offer_percentage >= 25 else 30
        elif signals.demand_level == DemandLevel.HIGH_DROP:
            score += 35 if decision.offer_percentage >= 20 else 25
        elif signals.demand_level == DemandLevel.LOW:
            score += 30 if decision.offer_percentage >= 20 else 20
        elif signals.demand_level == DemandLevel.HIGH:
            score += 25 if decision.offer_percentage >= 15 else 15
        else:
            score += 15

        # Demand alignment (30 points max)
        critical_actions = [ActionType.DISCOUNT, ActionType.URGENCY]
        if signals.demand_level in [DemandLevel.CRITICAL, DemandLevel.HIGH_DROP]:
            score += 30 if decision.action in critical_actions else 20
        elif signals.demand_level == DemandLevel.HIGH:
            score += 25 if decision.action == ActionType.URGENCY else 18
        else:
            score += 15

        # Customer LTV potential (30 points max)
        high_value_combos = [
            (CustomerType.NEW, ActionType.WELCOME),
            (CustomerType.INACTIVE, ActionType.REACTIVATION),
            (CustomerType.REGULAR, ActionType.LOYALTY),
        ]

        is_high_value = any(
            signals.customer_type == ct and decision.action == act
            for ct, act in high_value_combos
        )

        score += 30 if is_high_value else 12

        return min(score, 100)

    @staticmethod
    def score_message(decision: Decision, message: Message, signals: BusinessSignals) -> Dict:
        """
        FIXED: All sub-scores are 0-100, then weighted properly.
        """

        # Score each dimension (all 0-100 scale)
        decision_quality = ScoringEngine.score_decision_quality(decision, signals)
        personalization = ScoringEngine.score_personalization(decision, signals)
        clarity = ScoringEngine.score_clarity(decision, message)
        business_impact = ScoringEngine.score_business_impact(decision, signals)

        # Apply weights (now makes sense)
        total_score = (
            decision_quality * 0.40
            + personalization * 0.20
            + clarity * 0.15
            + business_impact * 0.25
        )

        message.quality_score = total_score

        return {
            "total": int(round(total_score)),
            "decision_quality": decision_quality,
            "personalization": personalization,
            "clarity": clarity,
            "business_impact": business_impact,
        }


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5: CATEGORY INTELLIGENCE
# ═════════════════════════════════════════════════════════════════════════════

class CategoryIntelligence:
    """Category-specific messaging and psychology."""

    RESTAURANT_TEMPLATES = {
        ActionType.WELCOME: "Welcome! Your first meal on us. Order now for {offer}% off.",
        ActionType.DISCOUNT: "We miss you! {offer}% off your next craving. Order now.",
        ActionType.LOYALTY: "Member exclusive: {offer}% off your favorite. Redeem today.",
        ActionType.UPSELL: "Complete your meal: Premium add-on {offer}% off.",
        ActionType.URGENCY: "🔥 Kitchen on fire! {offer}% off for next 2 hours.",
        ActionType.REACTIVATION: "Your favorite spot misses you. {offer}% off—come back today.",
        ActionType.REMINDER: "Remember our tasty meals? Order again for a treat.",
    }

    SALON_TEMPLATES = {
        ActionType.WELCOME: "First visit magic: {offer}% off any service. Book now.",
        ActionType.DISCOUNT: "Time for a refresh? {offer}% off your favorite service.",
        ActionType.LOYALTY: "VIP perk: {offer}% off your next appointment.",
        ActionType.UPSELL: "Elevate your look: Premium service {offer}% off.",
        ActionType.URGENCY: "Last-minute openings {offer}% off. Book your slot now.",
        ActionType.REACTIVATION: "We've missed you! Your beauty awaits: {offer}% off.",
        ActionType.REMINDER: "Time for your glow-up? Book an appointment today.",
    }

    GROCERY_TEMPLATES = {
        ActionType.WELCOME: "New shopper welcome: {offer}% off your first order.",
        ActionType.DISCOUNT: "Your essentials are on sale. {offer}% off this week.",
        ActionType.LOYALTY: "Member exclusive: {offer}% off on bulk purchases.",
        ActionType.UPSELL: "Stock up: Combo deals {offer}% off. Smart savings.",
        ActionType.URGENCY: "Flash sale: {offer}% off today only on essentials.",
        ActionType.REACTIVATION: "We've got your favorites back: {offer}% off today.",
        ActionType.REMINDER: "Fresh stock in! Your regular items await.",
    }

    FASHION_TEMPLATES = {
        ActionType.WELCOME: "Style starter kit: {offer}% off your first outfit.",
        ActionType.DISCOUNT: "New season, new you: {offer}% off trending styles.",
        ActionType.LOYALTY: "Exclusive early access: {offer}% off new arrivals.",
        ActionType.UPSELL: "Complete the look: Premium pieces {offer}% off.",
        ActionType.URGENCY: "Last sizes! Trending item {offer}% off—grab yours.",
        ActionType.REACTIVATION: "Your style evolved. Check out what's new: {offer}% off.",
        ActionType.REMINDER: "New drops in your style. Shop the latest.",
    }

    @staticmethod
    def get_template(category: Category, action: ActionType) -> str:
        templates = {
            Category.RESTAURANT: CategoryIntelligence.RESTAURANT_TEMPLATES,
            Category.SALON: CategoryIntelligence.SALON_TEMPLATES,
            Category.GROCERY: CategoryIntelligence.GROCERY_TEMPLATES,
            Category.FASHION: CategoryIntelligence.FASHION_TEMPLATES,
        }
        category_templates = templates.get(category, {})
        return category_templates.get(action, "Special offer for you: {offer}% off.")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6: MESSAGE GENERATOR
# ═════════════════════════════════════════════════════════════════════════════

class MessageGenerator:
    """Converts decision to natural message."""

    @staticmethod
    def generate_message(
        decision: Decision,
        signals: BusinessSignals,
        merchant_name: str = "Your Store",
    ) -> Message:
        """Generate final message."""

        template = CategoryIntelligence.get_template(signals.category, decision.action)
        message_body = template.replace("{offer}", str(decision.offer_percentage))

        if decision.personalization_level == "deep":
            prefix = f"Hi there! "
        else:
            prefix = ""

        urgency_level = (
            "high" if decision.priority >= 8
            else "medium" if decision.priority >= 5
            else "low"
        )

        conversion_impact = "strong" if decision.confidence_score >= 0.80 else "moderate" if decision.confidence_score >= 0.65 else "weak"

        final_message = f"{prefix}{message_body}\n\n→ {decision.cta_text}"

        return Message(
            content=final_message,
            decision=decision,
            quality_score=0.0,
            category_tone="category-specific",
            urgency_level=urgency_level,
            estimated_conversion_impact=conversion_impact,
        )


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 7: MAIN ORCHESTRATOR
# ═════════════════════════════════════════════════════════════════════════════

class AIComposer:
    """Main API."""

    @staticmethod
    def compose(
        category: str,
        merchant: str,
        trigger: str,
        customer: Optional[Dict] = None,
    ) -> Dict:
        """Main entry point."""

        try:
            category_enum = Category[category.upper()]
        except KeyError:
            raise ValueError(f"Invalid category: {category}")

        # Analyze
        signals = ContextAnalyzer.extract_signals(
            category_enum, merchant, trigger, customer
        )

        # Decide
        decision = DecisionEngine.make_decision(signals)

        # Generate
        message = MessageGenerator.generate_message(decision, signals, merchant)

        # Score
        score_result = ScoringEngine.score_message(decision, message, signals)

        # Package
        return {
            "merchant": merchant,
            "category": category,
            "trigger": trigger,
            "message": message.content,
            "decision": {
                "action": decision.action.value,
                "strategy": decision.strategy.value,
                "offer_percentage": decision.offer_percentage,
                "confidence": f"{decision.confidence_score:.0%}",
                "priority": decision.priority,
                "cta": decision.cta_text,
                "reasoning": decision.reasoning,
            },
            "quality": {
                "score": score_result["total"],
                "components": {
                    "decision_quality": score_result["decision_quality"],
                    "personalization": score_result["personalization"],
                    "clarity": score_result["clarity"],
                    "business_impact": score_result["business_impact"],
                },
            },
            "signals": {
                "customer_type": signals.customer_type.value,
                "demand_level": signals.demand_level.value,
                "time_context": signals.time_context.value,
                "urgency_level": message.urgency_level,
                "conversion_impact": message.estimated_conversion_impact,
            },
        }


# ═════════════════════════════════════════════════════════════════════════════
# EXECUTION
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 80)
    print("PRODUCTION AI DECISION INTELLIGENCE SYSTEM v2.0")
    print("OPTIMIZED - Fixed Scoring, Enhanced Strategy, Better Time Context")
    print("=" * 80)

    TEST_CASES = [
        {
            "name": "Test 1: Restaurant - Critical Demand Drop",
            "category": "restaurant",
            "merchant": "Vera's Bistro",
            "trigger": "critical_drop",
            "customer": None,
        },
        {
            "name": "Test 2: Restaurant - Peak Lunch Time (FIXED TIME)",
            "category": "restaurant",
            "merchant": "Vera's Bistro",
            "trigger": "peak_lunch_hour",
            "customer": {"days_since_last_purchase": 15, "value_tier": "regular"},
        },
        {
            "name": "Test 3: Salon - New Customer First Visit",
            "category": "salon",
            "merchant": "Glow Studio",
            "trigger": "welcome_offer",
            "customer": {"days_since_last_purchase": -1},
        },
        {
            "name": "Test 4: Salon - Inactive Customer Reactivation",
            "category": "salon",
            "merchant": "Glow Studio",
            "trigger": "low_traffic",
            "customer": {"days_since_last_purchase": 180, "value_tier": "atrisk"},
        },
        {
            "name": "Test 5: Grocery - Weekend VIP",
            "category": "grocery",
            "merchant": "Fresh & Co",
            "trigger": "weekend_promotion",
            "customer": {"days_since_last_purchase": 30, "value_tier": "vip"},
        },
        {
            "name": "Test 6: Fashion - Trending Item Low Stock",
            "category": "fashion",
            "merchant": "Style Haven",
            "trigger": "trending_item_low_stock",
            "customer": {"days_since_last_purchase": 7},
        },
        {
            "name": "Test 7: Restaurant - Dinner Rush VIP (URGENCY)",
            "category": "restaurant",
            "merchant": "Vera's Bistro",
            "trigger": "dinner_rush",
            "customer": {"days_since_last_purchase": 5, "value_tier": "vip"},
        },
        {
            "name": "Test 8: Grocery - Inactive Struggling",
            "category": "grocery",
            "merchant": "Fresh & Co",
            "trigger": "slow_traffic",
            "customer": {"days_since_last_purchase": 120, "value_tier": "standard"},
        },
        {
            "name": "Test 9: Fashion - Festival Launch",
            "category": "fashion",
            "merchant": "Style Haven",
            "trigger": "festival_launch",
            "customer": None,
        },
        {
            "name": "Test 10: Salon - Peak Booking VIP",
            "category": "salon",
            "merchant": "Glow Studio",
            "trigger": "peak_booking",
            "customer": {"days_since_last_purchase": 20, "value_tier": "vip"},
        },
    ]

    results = []
    for test in TEST_CASES:
        try:
            result = AIComposer.compose(
                category=test["category"],
                merchant=test["merchant"],
                trigger=test["trigger"],
                customer=test.get("customer"),
            )
            results.append((test["name"], result))
        except Exception as e:
            print(f"ERROR in {test['name']}: {e}")

    # Print results
    for test_name, result in results:
        print("\n" + "─" * 80)
        print(f"📊 {test_name}")
        print("─" * 80)
        print(f"\n💬 MESSAGE:\n{result['message']}")
        print(f"\n🎯 DECISION:")
        print(f"   • Action: {result['decision']['action']}")
        print(f"   • Strategy: {result['decision']['strategy']}")
        print(f"   • Offer: {result['decision']['offer_percentage']}%")
        print(f"   • Confidence: {result['decision']['confidence']}")
        print(f"   • Priority: {result['decision']['priority']}/10")
        print(f"\n⭐ QUALITY SCORE: {result['quality']['score']}/100")
        print(f"   • Decision Quality: {result['quality']['components']['decision_quality']}/100")
        print(f"   • Personalization: {result['quality']['components']['personalization']}/100")
        print(f"   • Clarity: {result['quality']['components']['clarity']}/100")
        print(f"   • Business Impact: {result['quality']['components']['business_impact']}/100")
        print(f"\n🔍 SIGNALS:")
        print(f"   • Customer Type: {result['signals']['customer_type']}")
        print(f"   • Demand: {result['signals']['demand_level']}")
        print(f"   • Time: {result['signals']['time_context']}")
        print(f"   • Urgency: {result['signals']['urgency_level']}")

    # Summary
    print("\n" + "=" * 80)
    print("📈 SYSTEM SUMMARY")
    print("=" * 80)
    scores = [r[1]["quality"]["score"] for r in results]
    print(f"\nTotal Tests: {len(results)}")
    print(f"Average Quality Score: {sum(scores) / len(scores):.1f}/100")
    print(f"Highest Score: {max(scores)}/100")
    print(f"Lowest Score: {min(scores)}/100")
    print(f"Score Distribution:")
    print(f"  • Excellent (80+): {sum(1 for s in scores if s >= 80)}")
    print(f"  • Good (70-79): {sum(1 for s in scores if 70 <= s < 80)}")
    print(f"  • Fair (60-69): {sum(1 for s in scores if 60 <= s < 70)}")
    print(f"  • Below Target (<60): {sum(1 for s in scores if s < 60)}")

    print("\n" + "=" * 80)
    print("✅ System v2.0 execution complete.")
    print("=" * 80)
