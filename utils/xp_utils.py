from schemas.khiladi import Khiladi

XP_PER_LEVEL = 1000

def calculate_level(total_xp: int, xp_debt: int = 0) -> int:
    """
    Calculate level from XP. 
    If total_xp is negative (user is in XP Debt / Shadow Realm), 
    they are 'Dishonored' and return Level 0.
    """
    if total_xp < 0:
        return 0
    return 1 + (total_xp // XP_PER_LEVEL)

def calculate_net_xp(total_xp: int, xp_debt: int) -> int:
    """Calculate net XP after accounting for debt."""
    net = total_xp - xp_debt
    return max(0, net)

def deduct_xp_penalty(khiladi: Khiladi, penalty_amount: int, session) -> Khiladi:
    """
    Deduct penalty XP from user. Handles XP debt creation.
    Returns the updated khiladi.
    """
    khiladi.total_xp -= penalty_amount
    khiladi.level = calculate_level(khiladi.total_xp, khiladi.xp_debt)
    session.add(khiladi)
    session.commit()
    session.refresh(khiladi)
    return khiladi

def sync_khiladi_xp(khiladi: Khiladi) -> Khiladi:
    """
    Recalculate and sync XP for a Khiladi after any XP change.
    Updates level based on current total_xp.
    """
    khiladi.level = calculate_level(khiladi.total_xp, khiladi.xp_debt)
    return khiladi
