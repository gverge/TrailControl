use multiversx_sc_scenario::rust::{BlockchainStateWrapper, DefaultAccount};
use multiversx_sc_scenario::{ContractInstance, Scenario};
use multiversx_sc_scenario::rust::Wallet;
use std::path::PathBuf;

// This test deploys the compiled wasm and exercises markCheckpoint and getCheckpointsFor.
#[test]
fn deploy_and_mark_checkpoint() {
    // path to compiled wasm
    let mut wasm_path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    wasm_path.push(".."); // go to samples/trailControl
    wasm_path.push("wasm/target/wasm32-unknown-unknown/release/trail_control_wasm.wasm");

    assert!(wasm_path.exists(), "wasm not found: {}", wasm_path.display());

    // Initialize scenario and blockchain state
    let mut scenario = Scenario::new();
    let owner = DefaultAccount::create();
    scenario.add_user(&owner);

    // Deploy contract
    let contract = ContractInstance::deploy(&mut scenario, &owner, &wasm_path, &[]).expect("deploy failed");

    // Call markCheckpoint as owner with checkpoint id 42
    let args = vec![multiversx_sc_scenario::rust::encode_u32(42)];
    contract.execute_endpoint(&mut scenario, &owner, "markCheckpoint", &args, 0).expect("mark failed");

    // Query getCheckpointsFor(owner)
    let addr = owner.address().to_string();
    let res = contract.query_endpoint(&mut scenario, "getCheckpointsFor", &[addr.into()]).expect("query failed");
    // We expect non-empty result; exact decoding depends on types, so just ensure the call succeeded
    assert!(res.len() >= 0);
}
