-- Minimal diagnostic of the original extractedTrace elimination scheme.
inductive AuditReach : Nat → Nat → Prop where
  | refl : ∀ x, AuditReach x x
  | step : ∀ x y z, AuditReach y z → AuditReach x z

def auditExtract : ∀ {x y}, AuditReach x y → List Nat
  | _, _, .refl _ => []
  | _, _, .step _ y _ rest => y :: auditExtract rest
