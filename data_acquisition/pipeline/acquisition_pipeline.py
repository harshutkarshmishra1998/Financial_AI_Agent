from typing import Dict

from data_acquisition.pipeline.acquisition_models import (
    AcquisitionResult,
    DomainExecutionRecord,
)
from data_acquisition.pipeline.domain_registry import DomainRegistry

import uuid
from data_acquisition.storage.snapshot_writer import (
    write_market_snapshot,
    write_news_snapshot,
    write_macro_snapshot
)


# class MultiDomainAcquisitionPipeline:
#     """
#     Executes acquisition across all requested domains.
#     """

#     def run(self, plan) -> AcquisitionResult:

#         result = AcquisitionResult(plan=plan)

#         for domain in plan.domains:

#             fetcher = DomainRegistry.get_fetcher(domain)

#             # -------------------------------------------------
#             # Domain not implemented yet
#             # -------------------------------------------------
#             if fetcher is None:
#                 result.execution_log.append(
#                     DomainExecutionRecord(
#                         domain=domain,
#                         success=False,
#                         message="Fetcher not implemented"
#                     )
#                 )
#                 continue

#             # -------------------------------------------------
#             # Execute domain fetch
#             # -------------------------------------------------
#             try:
#                 domain_data = fetcher.fetch(plan.assets, plan)

#                 result.domain_results[domain] = domain_data

#                 result.execution_log.append(
#                     DomainExecutionRecord(
#                         domain=domain,
#                         success=True,
#                         message="Fetched successfully"
#                     )
#                 )

#             except Exception as e:
#                 result.execution_log.append(
#                     DomainExecutionRecord(
#                         domain=domain,
#                         success=False,
#                         message=str(e)
#                     )
#                 )
#                 result.success = False

#         return result

class MultiDomainAcquisitionPipeline:

    def run(self, plan, query: dict | None = None):

        result = AcquisitionResult(plan=plan)

        # ---------------------------------
        # determine query_id
        # ---------------------------------
        query_id = None

        if query and "query_id" in query:
            query_id = query["query_id"]
        else:
            query_id = str(uuid.uuid4())

        result.query_id = query_id  # type: ignore

        # ---------------------------------
        # execute domains
        # ---------------------------------
        for domain in plan.domains:

            fetcher = DomainRegistry.get_fetcher(domain)

            if fetcher is None:
                result.execution_log.append(
                    DomainExecutionRecord(domain, False, "Fetcher not implemented")
                )
                continue

            try:
                domain_data = fetcher.fetch(plan.assets, plan)
                result.domain_results[domain] = domain_data

                result.execution_log.append(
                    DomainExecutionRecord(domain, True, "Fetched successfully")
                )

            except Exception as e:
                result.execution_log.append(
                    DomainExecutionRecord(domain, False, str(e))
                )
                result.success = False

        # ---------------------------------
        # SNAPSHOT PERSISTENCE
        # ---------------------------------
        if "market" in result.domain_results:
            write_market_snapshot(query_id, result.domain_results["market"])

        if "news" in result.domain_results:
            write_news_snapshot(query_id, result.domain_results["news"])

        if "macro" in result.domain_results:
            write_macro_snapshot(query_id, result.domain_results["macro"])

        return result