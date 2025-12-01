#![no_std]

use multiversx_sc::derive_imports::*;
use multiversx_sc::imports::*;

#[type_abi]
#[derive(NestedEncode, NestedDecode, TopEncode, TopDecode, ManagedVecItem, Clone)]
pub struct Checkpoint<M: ManagedTypeApi> {
    pub checkpoint_id: u32,
    pub timestamp: u64,
    pub _marker: ManagedBuffer<M>,
}

#[type_abi]
#[derive(TopEncode)]
pub struct CheckpointMarkedEvent {
    checkpoint_id: u32,
    timestamp: u64,
}

#[multiversx_sc::contract]
pub trait TrailControl {
    /// Mapping from wallet -> list of checkpoints (using storage key composition)
    #[storage_mapper("checkpoints")]
    fn checkpoints(&self, address: &ManagedAddress) -> VecMapper<Checkpoint<Self::Api>>;

    /// Set of wallets that have at least one checkpoint recorded
    #[storage_mapper("wallets")]
    fn wallets(&self) -> UnorderedSetMapper<ManagedAddress>;

    #[init]
    fn init(&self) {}

    /// Mark a checkpoint for the caller. Stores checkpoint id + current timestamp.
    #[endpoint(markCheckpoint)]
    fn mark_checkpoint(&self, checkpoint_id: u32) {
        let caller = self.blockchain().get_caller();
        let timestamp = self.blockchain().get_block_timestamp();

        let cp = Checkpoint {
            checkpoint_id,
            timestamp,
            _marker: ManagedBuffer::new(),
        };

        self.checkpoints(&caller).push(&cp);
        self.wallets().insert(caller.clone());
        self.checkpoint_marked_event(&caller, &CheckpointMarkedEvent { checkpoint_id, timestamp });
    }
    #[event("checkpointMarked")]
    fn checkpoint_marked_event(&self, #[indexed] address: &ManagedAddress, data: &CheckpointMarkedEvent);

    /// Returns the list of checkpoints for a given wallet.
    #[view(getCheckpointsFor)]
    fn get_checkpoints_for(
        &self,
        address: ManagedAddress,
    ) -> MultiValueEncoded<MultiValue2<u32, u64>> {
        let mut result = MultiValueEncoded::new();
        let vec_mapper = self.checkpoints(&address);
        let len = vec_mapper.len();
        for i in 1..=len {
            let cp = vec_mapper.get(i);
            result.push((cp.checkpoint_id, cp.timestamp).into());
        }
        result
    }

    /// Returns the list of wallets that have checkpoints.
    #[view(getAllWallets)]
    fn get_all_wallets(&self) -> ManagedVec<ManagedAddress> {
        let mut res = ManagedVec::new();
        for addr in self.wallets().iter() {
            res.push(addr);
        }
        res
    }
}
