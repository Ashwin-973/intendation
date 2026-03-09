import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Tuple, Any

'''can't understan shit!!'''

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('zion.tank')

@asynccontextmanager
async def extraction_context():
    """Context manager for extraction operations with proper cleanup"""
    logger.info("[TANK] Initializing extraction protocols...")
    try:
        yield
    except Exception as e:
        logger.error(f"[TANK] Critical failure in extraction context: {e}")
        raise
    finally:
        logger.info("[TANK] Extraction context terminated")

async def run_uplink() -> Dict[str, Any]:
    """Run parallel extractions with detailed error tracking"""
    operators = [("Trinity", 3000), ("Neo", 5000), ("Morpheus", 7000), ("Mouse", 2000)]
    results = {}
    
    async with asyncio.TaskGroup() as tg:
        tasks = {
            name: tg.create_task(
                extract_operator_signature(name, size),
                name=f"extract_{name.lower()}"
            )
            for name, size in operators
        }
    
    # This won't execute if TaskGroup fails, but shows the pattern
    for name, task in tasks.items():
        results[name] = task.result()
    
    return results

async def run_uplink_resilient() -> Dict[str, Any]:
    """Alternative: Continue extraction even if some operators fail"""
    operators = [("Trinity", 3000), ("Neo", 5000), ("Morpheus", 7000), ("Mouse", 2000)]
    
    # Use gather with return_exceptions for fault tolerance
    results = await asyncio.gather(
        *(extract_operator_signature(name, size) for name, size in operators),
        return_exceptions=True
    )
    
    extraction_report = {}
    for (name, _), result in zip(operators, results):
        if isinstance(result, Exception):
            logger.error(f"[TANK] {name} extraction failed: {type(result).__name__}: {result}")
            extraction_report[name] = {"status": "FAILED", "error": str(result)}
        else:
            logger.info(f"[TANK] {name} extracted successfully")
            extraction_report[name] = {"status": "SUCCESS", "data": result}
    
    return extraction_report

async def main():
    """Main extraction coordinator with comprehensive error handling"""
    async with extraction_context():
        try:
            # Use TaskGroup for fail-fast (current behavior)
            await run_uplink()
            logger.info("[TANK] All operators extracted successfully")
            
        except* ConnectionError as eg:
            # Handle Agent Smith interceptions specifically
            agent_failures = [str(e) for e in eg.exceptions if "Agent Smith" in str(e)]
            if agent_failures:
                logger.critical("[TANK] AGENT SMITH DETECTED! Severing compromised uplinks...")
                for failure in agent_failures:
                    logger.critical(f"[TANK] Compromised: {failure}")
                
                # Attempt emergency extraction of remaining operators
                logger.warning("[TANK] Attempting emergency extraction of uncompromised operators...")
                emergency_results = await run_uplink_resilient()
                
                successful_extractions = [
                    name for name, data in emergency_results.items() 
                    if data["status"] == "SUCCESS"
                ]
                
                if successful_extractions:
                    logger.info(f"[TANK] Emergency extraction successful for: {', '.join(successful_extractions)}")
                else:
                    logger.critical("[TANK] TOTAL MISSION FAILURE - All operators compromised")
                    
        except* Exception as eg:
            # Handle all other extraction failures
            logger.error(f"[TANK] Extraction operation failed with {len(eg.exceptions)} error(s):")
            
            for i, exc in enumerate(eg.exceptions, 1):
                logger.error(f"[TANK] Error {i}: {type(exc).__name__}: {exc}")
            
            # Attempt graceful degradation
            logger.warning("[TANK] Attempting fault-tolerant extraction...")
            try:
                fallback_results = await run_uplink_resilient()
                successful = sum(1 for r in fallback_results.values() if r["status"] == "SUCCESS")
                logger.info(f"[TANK] Fallback extraction completed: {successful}/{len(fallback_results)} operators saved")
            except Exception as fallback_error:
                logger.critical(f"[TANK] Fallback extraction failed: {fallback_error}")
                raise SystemExit("MISSION CRITICAL FAILURE - Zion compromised")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("[TANK] Extraction aborted by operator")
    except SystemExit as e:
        logger.critical(f"[TANK] System shutdown: {e}")
    except Exception as e:
        logger.critical(f"[TANK] Unexpected system failure: {type(e).__name__}: {e}")
        raise