class SemanticEngine:

    def analyze(self, text):

        tokens = text.lower().split()

        score = {
            "frontend": 0,
            "backend": 0,
            "database": 0
        }

        subtype = None

        frontend = ["ui", "page", "html", "css", "dashboard"]
        backend = ["api", "auth", "service", "endpoint"]
        database = ["db", "database", "table", "schema", "mysql", "sql"]

        for t in tokens:
            if t in frontend:
                score["frontend"] += 1
            if t in backend:
                score["backend"] += 1
            if t in database:
                score["database"] += 1

            # 🔴 SUBTYPE DETECTION
            if t == "api":
                subtype = "api"
            if t == "auth":
                subtype = "auth"

        best = max(score, key=score.get)
        confidence = score[best] / max(1, sum(score.values()))

        return {
            "type": best if score[best] > 0 else "generic",
            "subtype": subtype,
            "confidence": round(confidence, 2)
        }
