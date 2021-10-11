import deepmerge


class StrategicMerger(deepmerge.Merger):
    key = "name"
    strategyKey = "$mergeStrategy"

    def __init__(self, keyname: str, type_strategies, fallback_strategies, type_conflict_strategies):
        self.key = keyname
        super().__init__(type_strategies, fallback_strategies, type_conflict_strategies)


def strategic_array_merge(
    merger: StrategicMerger,
    path,
    base_value: list,
    value_to_merge_in: list,
):
    # both base_value and value_to_merge_in should be lists
    for element in value_to_merge_in:
        if merger.key not in element:
            # that means a generic not named array, so override it
            return value_to_merge_in

        else:
            already_exists = list(
                filter(
                    lambda x: x[1][merger.key] == element[merger.key],
                    enumerate(base_value),
                )
            )
            if len(already_exists) > 0:
                mergeStrategy = element.pop(merger.strategyKey, "").lower()
                if mergeStrategy == "remove":
                    base_value.remove(already_exists[0][1])
                    continue
                elif mergeStrategy == "replace":
                    base_value[already_exists[0][0]] = element
                else:
                    base_value[already_exists[0][0]] = merger.value_strategy(
                        path + [already_exists[0][0]],
                        already_exists[0][1],
                        element,
                    )
            else:
                base_value.append(element)
    return base_value


def get_strategic_merger(keyname: str = "name"):
    return StrategicMerger(
        # strategy lookup key
        keyname,
        # strategies
        [
            (list, strategic_array_merge),
            (dict, ["merge"]),
            (set, ["union"]),
        ],
        # fallback
        ["override"],
        # type conflict
        ["override"],
    )
